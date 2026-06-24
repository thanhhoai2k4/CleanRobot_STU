import os

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

from webots_ros2_driver.webots_launcher import WebotsLauncher
from webots_ros2_driver.webots_controller import WebotsController


def generate_launch_description():
    world = PathJoinSubstitution([
        FindPackageShare('clean_robot_simulation'),
        'worlds',
        'clean_room.wbt'
    ])

    robot_description = Command([
        'xacro ',
        PathJoinSubstitution([
            FindPackageShare('clean_robot_description'),
            'urdf',
            'clean_robot.urdf.xacro'
        ])
    ])

    ros2_control_params = PathJoinSubstitution([
        FindPackageShare('clean_robot_simulation'),
        'config',
        'ros2_control.yaml'
    ])

    webots = WebotsLauncher(
        world=world
    )

    robot_driver = WebotsController(
        robot_name='my_robot',
        parameters=[
            {'robot_description': robot_description},
            ros2_control_params,
            {'use_sim_time': True}
        ]
    )

    joint_state_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen'
    )

    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller'],
        output='screen'
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[
            {'robot_description': robot_description},
            {'use_sim_time': True}
        ],
        output='screen'
    )

    return LaunchDescription([
        webots,
        robot_state_publisher,
        robot_driver,
        joint_state_spawner,
        diff_drive_spawner,
    ])