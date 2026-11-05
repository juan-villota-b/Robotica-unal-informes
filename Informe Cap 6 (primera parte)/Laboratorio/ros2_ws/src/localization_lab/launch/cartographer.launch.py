"""Lanza Cartographer ROS2 sobre el TurtleBot3 simulado.

Réplica de la guía CAP6 (paso 14): nodo de SLAM y servidor de mapa de ocupación,
con ``use_sim_time`` y ``resolution`` configurables por argumento de launch.

Requiere ``cartographer_ros``, que no está publicado para ROS 2 *lyrical*: en
ese caso usar ``slam_toolbox.launch.py`` (mismo pipeline LiDAR -> /map).
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    config_dir = os.path.join(
        get_package_share_directory('localization_lab'),
        'config'
    )

    use_sim_time = LaunchConfiguration('use_sim_time')
    resolution = LaunchConfiguration('resolution')

    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time}
        ],
        arguments=[
            '-configuration_directory', config_dir,
            '-configuration_basename', 'cartographer.lua'
        ]
    )

    occupancy_grid_node = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time}
        ],
        arguments=[
            '-resolution', resolution
        ]
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
        cartographer_node,
        occupancy_grid_node
    ])
