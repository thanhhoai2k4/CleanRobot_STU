import rclpy

from rclpy.node import Node

from std_msgs.msg import String

from geometry_msgs.msg import PoseStamped, Twist

from .state_machine import MissionState

from .nav2_client import Nav2Client

from .target_store import TargetStore

class MissionManagerNode(Node):

    def __init__(self):
        super().__init__('mission_manager_node')

        self.declare_parameter(
            'search_linear_speed',
            0.0
        )
        self.declare_parameter(
            'search_angular_speed',
            0.35
        )

        self.state_pub = self.create_publisher(
            String,
            '/mission/state',
            10
        )
        self.event_pub = self.create_publisher(
            String,
            '/mission/event',
            10
        )
        self.rejected_target_pub = self.create_publisher(
            String,
            '/trash/rejected_id',
            10
        )
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.target_sub = self.create_subscription(
            PoseStamped,
            '/trash/target_pose',
            self.target_callback,
            10
        )
        self.target_id_sub = self.create_subscription(
            String,
            '/trash/target_id',
            self.target_id_callback,
            10
        )

        self.nav2 = Nav2Client(self)
        self.target_store = TargetStore()
        self.current_target_id = ''
        self.search_linear_speed = float(
            self.get_parameter('search_linear_speed').value
        )
        self.search_angular_speed = float(
            self.get_parameter('search_angular_speed').value
        )
        
        self.state = MissionState.SEARCHING
        self.publish_state()

        # Rhythmic control loop execution running at 10Hz
        self.control_timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info('MissionManagerNode started')

    def publish_state(self):
        msg = String()
        msg.data = self.state.value
        self.state_pub.publish(msg)

    def change_state(self, new_state):
        self.get_logger().info(f'{self.state.value} -> {new_state.value}')
        self.state = new_state
        self.publish_state()

    def target_callback(self, pose):
        # Safe ingestion: ignore incoming frames if mid-transit
        if self.state == MissionState.NAVIGATING_TO_TRASH:
            return
        
        self.target_store.set_target(pose)

    def target_id_callback(self, msg):
        if self.state == MissionState.NAVIGATING_TO_TRASH:
            return

        self.current_target_id = msg.data

    def control_loop(self):
        """Centralized, non-blocking execution state machine."""
        if self.state == MissionState.SEARCHING:
            target = self.target_store.get_target()
            if target is not None:
                self.publish_stop()
                if self.nav2.send_goal(target):
                    self.change_state(MissionState.NAVIGATING_TO_TRASH)
            else:
                self.publish_search_motion()

        elif self.state == MissionState.NAVIGATING_TO_TRASH:
            nav2_status = self.nav2.get_status()
            if nav2_status in (
                Nav2Client.SENDING,
                Nav2Client.ACTIVE
            ):
                return

            if nav2_status == Nav2Client.SUCCEEDED:
                self.change_state(MissionState.REACHED_TRASH)
            elif nav2_status in (
                Nav2Client.FAILED,
                Nav2Client.REJECTED,
                Nav2Client.CANCELED
            ):
                self.change_state(MissionState.FAILED)

        elif self.state == MissionState.REACHED_TRASH:
            self.publish_stop()
            self.publish_event('REACHED_TRASH')
            self.nav2.reset()
            self.target_store.clear()
            self.current_target_id = ''
            self.change_state(MissionState.SEARCHING)

        elif self.state == MissionState.FAILED:
            self.publish_stop()
            self.publish_rejected_target()
            self.publish_event('FAILED_TARGET')
            self.nav2.reset()
            self.target_store.clear()
            self.current_target_id = ''
            self.change_state(MissionState.SEARCHING)

    def publish_search_motion(self):
        twist = Twist()
        twist.linear.x = self.search_linear_speed
        twist.angular.z = self.search_angular_speed
        self.cmd_vel_pub.publish(twist)

    def publish_stop(self):
        self.cmd_vel_pub.publish(Twist())

    def publish_event(self, event_name):
        msg = String()
        if self.current_target_id:
            msg.data = f'{event_name}:{self.current_target_id}'
        else:
            msg.data = event_name
        self.event_pub.publish(msg)

    def publish_rejected_target(self):
        if not self.current_target_id:
            return

        msg = String()
        msg.data = self.current_target_id
        self.rejected_target_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = MissionManagerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
