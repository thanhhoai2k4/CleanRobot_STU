import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.events import matches_action
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import LifecycleNode, Node
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from launch.actions import EmitEvent, LogInfo, RegisterEventHandler
from lifecycle_msgs.msg import Transition


def generate_launch_description():
    pkg_navigation = get_package_share_directory('clean_robot_navigation')
    default_slam_params_file = os.path.join(pkg_navigation, 'config', 'slam_params.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    slam_params_file = LaunchConfiguration('slam_params_file')
    autostart = LaunchConfiguration('autostart')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Dùng thời gian mô phỏng Webots'
    )

    declare_slam_params = DeclareLaunchArgument(
        'slam_params_file',
        default_value=default_slam_params_file,
        description='Đường dẫn tới file cấu hình SLAM yaml'
    )

    declare_autostart = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Tự configure và activate slam_toolbox'
    )

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

    slam_toolbox_node = LifecycleNode(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        namespace='',
        output='screen',
        parameters=[
            slam_params_file,
            {
                'use_sim_time': use_sim_time,
                'odom_frame': 'odom',
                'map_frame': 'map',
                'base_frame': 'base_footprint',
                'scan_topic': '/scan_normalized',
                'mode': 'mapping',
                'use_lifecycle_manager': False,
            }
        ],
    )

    configure_event = EmitEvent(
        event=ChangeState(
            lifecycle_node_matcher=matches_action(slam_toolbox_node),
            transition_id=Transition.TRANSITION_CONFIGURE
        ),
        condition=IfCondition(autostart)
    )

    activate_event = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=slam_toolbox_node,
            start_state='configuring',
            goal_state='inactive',
            entities=[
                LogInfo(msg='[clean_robot_navigation] Activating slam_toolbox.'),
                EmitEvent(event=ChangeState(
                    lifecycle_node_matcher=matches_action(slam_toolbox_node),
                    transition_id=Transition.TRANSITION_ACTIVATE
                ))
            ]
        ),
        condition=IfCondition(autostart)
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_slam_params,
        declare_autostart,
        scan_normalizer_node,
        slam_toolbox_node,
        configure_event,
        activate_event,
    ])
