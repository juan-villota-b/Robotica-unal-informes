"""Mundo del laboratorio con el modelo del burger estabilizado.

Es el mismo ``turtlebot3_world`` de la guía, pero spawnea el modelo que está en
``models/turtlebot3_burger`` de este paquete, con dos correcciones de
estabilidad (ver ``models/turtlebot3_burger/model.sdf``):

* la rueda loca apoya 1 mm más bajo, así el robot tiene los tres puntos de
  apoyo de verdad y no se mece entre dos ruedas y el caster;
* la fricción de las ruedas baja de 100000 a 1.0, que es goma contra piso:
  con fricción infinita el robot no puede patinar al girar en el lugar y se
  voltea.

El resto (mundo, bridge, robot_state_publisher) es lo mismo que trae
``turtlebot3_gazebo``.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('localization_lab')
    tb_gazebo = get_package_share_directory('turtlebot3_gazebo')
    ros_gz_sim = get_package_share_directory('ros_gz_sim')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    x_pose = LaunchConfiguration('x_pose', default='-2.0')
    y_pose = LaunchConfiguration('y_pose', default='-0.5')

    world = os.path.join(tb_gazebo, 'worlds', 'turtlebot3_world.world')
    model = os.path.join(
        pkg_share, 'models', 'turtlebot3_burger', 'model.sdf')
    bridge_params = os.path.join(
        tb_gazebo, 'params', 'turtlebot3_burger_bridge.yaml')

    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': ['-r -s -v2 ', world],
            'on_exit_shutdown': 'true'
        }.items()
    )

    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': '-g -v2 ',
            'on_exit_shutdown': 'true'
        }.items()
    )

    spawn_cmd = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'burger',
            '-file', model,
            '-x', x_pose,
            '-y', y_pose,
            '-z', '0.01'
        ],
        output='screen',
    )

    bridge_cmd = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '--ros-args',
            '-p',
            'config_file:=' + bridge_params,
        ],
        output='screen',
    )

    robot_state_publisher_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(tb_gazebo, 'launch', 'robot_state_publisher.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # Los meshes del modelo (model://turtlebot3_common/...) los resuelve Gazebo
    # con esta ruta; el mundo también los usa.
    set_env_vars = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        os.path.join(tb_gazebo, 'models')
    )

    return LaunchDescription([
        gzserver_cmd,
        gzclient_cmd,
        spawn_cmd,
        bridge_cmd,
        robot_state_publisher_cmd,
        set_env_vars,
    ])
