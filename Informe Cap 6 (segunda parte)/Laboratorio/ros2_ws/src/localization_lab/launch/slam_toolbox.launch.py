"""Lanza SLAM Toolbox sobre el TurtleBot3 simulado.

Sustituto de ``cartographer.launch.py``: ``cartographer_ros`` no está publicado
para ROS 2 *lyrical*, así que el laboratorio usa SLAM Toolbox, que cubre el
mismo pipeline de la guía CAP6 (pasos §13–§21): LiDAR ``/scan`` -> SLAM ->
``/map`` y TF ``map->odom``.

La interfaz imita a la del launch de la guía (paso 14): ``use_sim_time`` y
``resolution`` configurables. El guardado del mapa (§25) sigue siendo
``ros2 run nav2_map_server map_saver_cli -f <nombre>``.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    EmitEvent,
    LogInfo,
    RegisterEventHandler,
)
from launch.conditions import IfCondition
from launch.events import matches_action
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import LifecycleNode
from launch_ros.descriptions import ParameterFile, ParameterValue
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition


def generate_launch_description():
    autostart = LaunchConfiguration('autostart')
    use_sim_time = LaunchConfiguration('use_sim_time')
    resolution = LaunchConfiguration('resolution')
    slam_params_file = LaunchConfiguration('slam_params_file')

    default_params_file = os.path.join(
        get_package_share_directory('localization_lab'),
        'config',
        'slam_toolbox.yaml'
    )

    slam_toolbox_node = LifecycleNode(
        parameters=[
            ParameterFile(slam_params_file, allow_substs=True),
            {
                'use_sim_time': ParameterValue(use_sim_time, value_type=bool),
                'resolution': ParameterValue(resolution, value_type=float),
            },
        ],
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        namespace=''
    )

    configure_event = EmitEvent(
        event=ChangeState(
            lifecycle_node_matcher=matches_action(slam_toolbox_node),
            transition_id=Transition.TRANSITION_CONFIGURE
        ),
        condition=IfCondition(autostart)
    )

    activate_event = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=slam_toolbox_node,
            start_state='configuring',
            goal_state='inactive',
            entities=[
                LogInfo(msg='[localization_lab] Activando SLAM Toolbox.'),
                EmitEvent(event=ChangeState(
                    lifecycle_node_matcher=matches_action(slam_toolbox_node),
                    transition_id=Transition.TRANSITION_ACTIVATE
                ))
            ]
        ),
        condition=IfCondition(autostart)
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Usar el reloj de Gazebo (/clock)'
        ),
        DeclareLaunchArgument(
            'resolution',
            default_value='0.05',
            description='Resolución del mapa de ocupación [m/celda]'
        ),
        DeclareLaunchArgument(
            'slam_params_file',
            default_value=default_params_file,
            description='Ruta al YAML de parámetros de SLAM Toolbox'
        ),
        DeclareLaunchArgument(
            'autostart',
            default_value='true',
            description='Configurar y activar el nodo automáticamente'
        ),
        slam_toolbox_node,
        configure_event,
        activate_event
    ])
