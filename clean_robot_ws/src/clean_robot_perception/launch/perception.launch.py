from launch import LaunchDescription

from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([

        Node(
            package='clean_robot_perception',
            executable='trash_detector_node',
            output='screen'
        ),

        Node(
            package='clean_robot_perception',
            executable='trash_localization_node',
            output='screen'
        ),

        Node(
            package='clean_robot_perception',
            executable='trash_tracker_node',
            output='screen'
        )

    ])