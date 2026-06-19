import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    pkg_navigation = get_package_share_directory('clean_robot_navigation')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')
    
    # Đường dẫn file config yaml
    nav2_yaml_path = os.path.join(pkg_navigation, 'config', 'nav2_params.yaml')
    
    # Sử dụng lại file launch chuẩn của hệ thống nhưng nạp tham số tùy biến của xe mình
    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'params_file': nav2_yaml_path,
            'use_sim_time': 'True'
        }.items()
    )

    return LaunchDescription([
        nav2_bringup_launch
    ])