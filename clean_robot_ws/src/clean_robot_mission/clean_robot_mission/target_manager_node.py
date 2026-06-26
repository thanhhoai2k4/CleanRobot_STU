import rclpy

from rclpy.node import Node

from std_msgs.msg import String

from geometry_msgs.msg import PoseStamped

from clean_robot_msgs.msg import TrashCandidateArray

class TargetManagerNode(Node):

    def __init__(self):
        super().__init__('target_manager_node')

        self.declare_parameter(
            'candidate_topic',
            '/trash/tracked_candidates'
        )
        self.rejected_targets = set()

        self.subscription = self.create_subscription(
            TrashCandidateArray,
            self.get_parameter('candidate_topic').value,
            self.candidate_callback,
            10
        )

        self.rejected_subscription = self.create_subscription(
            String,
            '/trash/rejected_id',
            self.rejected_callback,
            10
        )

        self.target_pose_pub = self.create_publisher(
            PoseStamped,
            '/trash/target_pose',
            10
        )

        self.target_id_pub = self.create_publisher(
            String,
            '/trash/target_id',
            10
        )

        self.get_logger().info('TargetManagerNode started')

    def rejected_callback(self, msg):
        if msg.data:
            self.rejected_targets.add(msg.data)

    def candidate_callback(self, msg):
        if len(msg.candidates) == 0:
            return

        reachable = [
            c for c in msg.candidates
            if c.reachable and c.id not in self.rejected_targets
        ]
        if len(reachable) == 0:
            return

        best = max(reachable, key=lambda x: x.confidence)

        target_id = String()
        target_id.data = best.id
        self.target_id_pub.publish(target_id)

        self.target_pose_pub.publish(best.pose)

        self.get_logger().info(f'Selected target: {best.id}')

def main(args=None):
    rclpy.init(args=args)
    node = TargetManagerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
