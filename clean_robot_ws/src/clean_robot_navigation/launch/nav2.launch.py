import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_navigation = get_package_share_directory('clean_robot_navigation')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    use_sim_time = LaunchConfiguration('use_sim_time')
    map_path = LaunchConfiguration('map')
    autostart = LaunchConfiguration('autostart')

    nav2_yaml_path = os.path.join(pkg_navigation, 'config', 'nav2_params.yaml')
    default_map_path = os.path.join(pkg_navigation, 'maps', 'my_map.yaml')

    scan_normalizer_node = Node(
        package='clean_robot_navigation',
        executable='scan_normalizer_node.py',
        name='scan_normalizer_node',
        output='screen',
        parameters=[{
            'input_topic': '/scan',
            'output_topic': '/scan_normalized',
            'use_sim_time': use_sim_time,
        }],
    )

    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': map_path,
            'params_file': nav2_yaml_path,
            'use_sim_time': use_sim_time,
            'autostart': autostart,
            'slam': 'False',
            'use_localization': 'True',
            'use_composition': 'False',
        }.items()
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use Webots simulation time'
        ),
        DeclareLaunchArgument(
            'map',
            default_value=default_map_path,
            description='Static map yaml file for Nav2 localization'
        ),
        DeclareLaunchArgument(
            'autostart',
            default_value='true',
            description='Automatically activate Nav2 lifecycle nodes'
        ),
        scan_normalizer_node,
        nav2_bringup_launch
    ])
