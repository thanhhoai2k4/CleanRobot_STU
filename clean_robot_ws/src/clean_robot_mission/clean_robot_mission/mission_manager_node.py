import rclpy

from rclpy.node import Node

from std_msgs.msg import String

from geometry_msgs.msg import PoseStamped

from .state_machine import MissionState

from .nav2_client import FakeNav2Client

from .target_store import TargetStore

from .search_behavior import SearchBehavior

class MissionManagerNode(Node):

    def __init__(self):
        super().__init__('mission_manager_node')

        self.state_pub = self.create_publisher(
            String,
            '/mission/state',
            10
        )

        self.target_sub = self.create_subscription(
            PoseStamped,
            '/trash/target_pose',
            self.target_callback,
            10
        )

        self.nav2 = FakeNav2Client()
        self.target_store = TargetStore()
        self.search_behavior = SearchBehavior()
        
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

    def control_loop(self):
        """Centralized, non-blocking execution state machine."""
        if self.state == MissionState.SEARCHING:
            target = self.target_store.get_target()
            if target is not None:
                self.change_state(MissionState.NAVIGATING_TO_TRASH)
            else:
                # Optional: Handle search behavior waypoint tracking here
                pass

        elif self.state == MissionState.NAVIGATING_TO_TRASH:
            target = self.target_store.get_target()
            if target is not None:
                success = self.nav2.send_goal(target)
                if success:
                    self.change_state(MissionState.REACHED_TRASH)
                else:
                    self.change_state(MissionState.FAILED)

        elif self.state == MissionState.REACHED_TRASH:
            # Task completed, wipe memory slot and return to search
            self.target_store.clear()
            self.change_state(MissionState.SEARCHING)

        elif self.state == MissionState.FAILED:
            self.target_store.clear()
            self.change_state(MissionState.SEARCHING)

def main(args=None):
    rclpy.init(args=args)
    node = MissionManagerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()