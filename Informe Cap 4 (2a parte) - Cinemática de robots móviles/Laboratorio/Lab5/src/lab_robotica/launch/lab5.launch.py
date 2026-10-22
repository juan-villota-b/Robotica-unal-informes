"""
Lanzador del laboratorio: un solo comando arranca Gazebo con el TurtleBot3, el
nodo de la actividad y RViz configurado (Fixed Frame odom, RobotModel y el
rastro de la trayectoria sobre /odom).

    ros2 launch lab_robotica lab5.launch.py actividad:=3

Opciones:
    actividad   3 (seguimiento de linea), 4 (Pure Pursuit) o 5 (ir a un punto)
    rviz        true (por defecto) -> abre ademas RViz

Dos detalles pensados para que no falle:

  * la GUI de Gazebo se lanza como proceso normal (no obligatorio), de modo que
    cerrarla no tumba la simulacion ni a RViz, y
  * RViz arranca unos segundos despues de Gazebo: si las dos interfaces graficas
    inicializan OpenGL al mismo tiempo, una de las dos se cae.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (AppendEnvironmentVariable, DeclareLaunchArgument,
                            ExecuteProcess, IncludeLaunchDescription,
                            OpaqueFunction, SetEnvironmentVariable, TimerAction)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

# Nodo ROS2 que resuelve cada actividad.
NODOS = {
    '3': 'act3_linea_turtlebot3',
    '4': 'act4_pure_pursuit_turtlebot3',
    '5': 'act5_go_to_goal',
}

RETARDO_RVIZ = 6.0   # s: deja que Gazebo termine de inicializar OpenGL
# s: el nodo espera a que RViz ya este conectado, para que el recorrido se
# dibuje desde el principio (en la actividad 5 el robot llega al objetivo en
# pocos segundos y si no, RViz no alcanza a dibujarlo).
RETARDO_NODO = 10.0


def lanzar_nodo(contexto, *args):
    """Arranca el nodo de la actividad pedida y avisa si el numero no existe."""
    actividad = contexto.launch_configurations['actividad']
    if actividad not in NODOS:
        raise RuntimeError(f'actividad "{actividad}" no existe; usa 3, 4 o 5')
    return [Node(
        package='lab_robotica',
        executable=NODOS[actividad],
        output='screen',
    )]


def generate_launch_description():
    """Gazebo (servidor, robot, puente y GUI) + nodo de la actividad + RViz."""
    pkg = get_package_share_directory('lab_robotica')
    tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')

    mundo = os.path.join(tb3_gazebo, 'worlds', 'empty_world.world')
    modelo = os.path.join(tb3_gazebo, 'models', 'turtlebot3_burger', 'model.sdf')
    puente = os.path.join(tb3_gazebo, 'params', 'turtlebot3_burger_bridge.yaml')

    return LaunchDescription([
        DeclareLaunchArgument('actividad', default_value='3',
                              description='3: linea, 4: pure pursuit, 5: ir a un punto'),
        DeclareLaunchArgument('rviz', default_value='true'),

        # Sin esto el lanzamiento de TurtleBot3 falla con "'TURTLEBOT3_MODEL'".
        SetEnvironmentVariable('TURTLEBOT3_MODEL', 'burger'),
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH',
                                  os.path.join(tb3_gazebo, 'models')),

        # Descubrimiento DDS solo por loopback. Con el valor por defecto (SUBNET)
        # y varias interfaces virtuales (docker0, br-*, veth*) el nodo y el
        # puente ros_gz a veces no se descubren: el puente queda conectado a
        # Gazebo pero no recibe /cmd_vel ni publica /odom, y el robot no se mueve.
        SetEnvironmentVariable('ROS_AUTOMATIC_DISCOVERY_RANGE', 'LOCALHOST'),
        SetEnvironmentVariable('ROS_LOCALHOST_ONLY', '1'),

        # Servidor de fisica (sin GUI). Va como proceso propio: no depende de
        # la ventana, asi cerrarla no lo mata.
        ExecuteProcess(cmd=['gz', 'sim', '-r', '-s', '-v2', mundo], output='screen'),

        # El TurtleBot3 en el origen del mundo.
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-name', 'turtlebot3', '-file', modelo, '-z', '0.01'],
            output='screen',
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(
                tb3_gazebo, 'launch', 'robot_state_publisher.launch.py')),
            launch_arguments={'use_sim_time': 'true'}.items(),
        ),

        # Puente ros_gz: /odom, /cmd_vel, /tf, /scan, /imu y /clock.
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=['--ros-args', '-p', 'config_file:=' + puente],
            output='screen',
        ),

        # GUI de Gazebo: proceso propio, independiente del servidor.
        ExecuteProcess(cmd=['gz', 'sim', '-g', '-v2'], output='screen'),

        # RViz despues que Gazebo, para no competir por OpenGL.
        TimerAction(period=RETARDO_RVIZ, actions=[
            Node(
                package='rviz2',
                executable='rviz2',
                name='rviz2',
                arguments=['-d', os.path.join(pkg, 'config', 'lab5.rviz')],
                parameters=[{'use_sim_time': True}],
                output='screen',
                condition=IfCondition(LaunchConfiguration('rviz')),
            ),
        ]),

        # El nodo arranca despues: asi RViz ya esta dibujando cuando el robot
        # empieza a moverse y se ve la trayectoria completa.
        TimerAction(period=RETARDO_NODO, actions=[
            OpaqueFunction(function=lanzar_nodo),
        ]),
    ])
