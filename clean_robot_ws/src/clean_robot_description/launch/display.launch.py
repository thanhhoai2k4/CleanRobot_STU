import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node

def generate_launch_description():
    pkg_description = get_package_share_directory('clean_robot_description')
    
    # Đường dẫn đến file xacro tổng
    xacro_file = os.path.join(pkg_description, 'urdf', 'clean_robot.urdf.xacro')
    
    # Đọc cấu trúc robot thông qua xacro command
    robot_description_raw = Command(['xacro ', xacro_file])
    
    # Node xuất bản trạng thái tọa độ TF hệ thống
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_raw}]
    )
    
    # Node mở giao diện đồ họa RViz2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher_node,
        rviz_node
    ])
