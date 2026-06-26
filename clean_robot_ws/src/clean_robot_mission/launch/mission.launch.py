from launch import LaunchDescription

from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([

        Node(
            package='clean_robot_mission',
            executable='target_manager_node',
            output='screen',
            parameters=[
                {'use_sim_time': True}
            ]
        ),

        Node(
            package='clean_robot_mission',
            executable='mission_manager_node',
            output='screen',
            parameters=[
                {'use_sim_time': True}
            ]
        )

    ])
