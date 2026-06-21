import os
import launch
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from webots_ros2_driver.webots_controller import WebotsController
from webots_ros2_driver.webots_launcher import WebotsLauncher

def generate_launch_description():
    package_dir = get_package_share_directory('clean_robot_simulation')

    # Trỏ đúng tới file cấu hình urdf trong folder resource
    robot_description_path = os.path.join(package_dir, 'resource', 'my_robot.urdf')
    
    # Trỏ tới file môi trường .wbt
    world_path = os.path.join(package_dir, 'worlds', 'my_world.wbt')

    # 1. Khởi động môi trường Webots
    webots = WebotsLauncher(
        world=world_path
    )

    # 2. Khai báo Driver kết nối với Webots
    my_robot_driver = WebotsController(
        robot_name='my_robot', # Lưu ý: Tên này phải trùng với thuộc tính "name" của con robot trong file my_world.wbt
        parameters=[
            {'robot_description': robot_description_path},
            {'use_sim_time': True} 
        ]
    )

    # 3. Khởi động Node điều khiển tay (file clean_robot_simulation.py của bạn)
    manual_cmd_node = Node(
        package='clean_robot_simulation',
        executable='simulation_test_node',
        name='manual_cmd_node',
        output='screen'
    )

    return LaunchDescription([
        webots,
        my_robot_driver,
        manual_cmd_node,
        
        # Cấu hình tự động tắt ROS 2 khi bạn bấm tắt phần mềm Webots
        launch.actions.RegisterEventHandler(
            event_handler=launch.event_handlers.OnProcessExit(
                target_action=webots,
                on_exit=[launch.actions.EmitEvent(event=launch.events.Shutdown())],
            )
        )
    ])