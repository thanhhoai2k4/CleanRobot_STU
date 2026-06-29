import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_navigation = get_package_share_directory('clean_robot_navigation')
    pkg_simulation = get_package_share_directory('clean_robot_simulation')
    pkg_perception = get_package_share_directory('clean_robot_perception')
    pkg_mission = get_package_share_directory('clean_robot_mission')

    use_sim_time = LaunchConfiguration('use_sim_time')
    map_path = LaunchConfiguration('map')

    simulation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_simulation, 'launch', 'robot_launch.py')
        )
    )

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_navigation, 'launch', 'nav2.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'map': map_path,
        }.items()
    )

    perception_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_perception, 'launch', 'perception.launch.py')
        )
    )

    mission_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_mission, 'launch', 'mission.launch.py')
        )
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use Webots simulation time'
        ),
        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(pkg_navigation, 'maps', 'my_map.yaml'),
            description='Static map yaml file for Nav2 localization'
        ),
        simulation_launch,
        nav2_launch,
        perception_launch,
        mission_launch,
    ])
