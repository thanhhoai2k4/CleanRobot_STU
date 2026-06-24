import os

if 'WEBOTS_HOME' not in os.environ:
    if os.path.exists('/snap/webots/current/usr/share/webots'):
        os.environ['WEBOTS_HOME'] = '/snap/webots/current/usr/share/webots'
    elif os.path.exists('/usr/local/webots'):
        os.environ['WEBOTS_HOME'] = '/usr/local/webots'
    else:
        raise RuntimeError(
            'WEBOTS_HOME is not set. Please export WEBOTS_HOME first.'
        )

import launch
from launch import LaunchDescription
from launch.actions import RegisterEventHandler, EmitEvent
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.substitutions import Command

from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

from webots_ros2_driver.webots_controller import WebotsController
from webots_ros2_driver.webots_launcher import WebotsLauncher


def generate_launch_description():
    sim_dir = get_package_share_directory('clean_robot_simulation')
    desc_dir = get_package_share_directory('clean_robot_description')

    world_path = os.path.join(sim_dir, 'worlds', 'my_world.wbt')
    xacro_file = os.path.join(desc_dir, 'urdf', 'clean_robot.urdf.xacro')

    robot_description_content = Command([
        'xacro ',
        xacro_file
    ])

    webots = WebotsLauncher(
        world=world_path, 
        ros2_supervisor=True
    )


    my_robot_driver = WebotsController(
        robot_name='my_robot',
        parameters=[
            {'robot_description': robot_description_content},
            {'use_sim_time': True}
        ]
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_description_content},
            {'use_sim_time': True}
        ]
    )

    manual_cmd_node = Node(
        package='clean_robot_simulation',
        executable='simulation_test_node',
        name='manual_cmd_node',
        output='screen',
        parameters=[
            {'use_sim_time': True}
        ]
    )

    shutdown_handler = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=webots,
            on_exit=[
                EmitEvent(event=Shutdown())
            ],
        )
    )

    return LaunchDescription([
        webots,
        webots._supervisor,
        my_robot_driver,
        robot_state_publisher_node,
        manual_cmd_node,
        shutdown_handler
    ])