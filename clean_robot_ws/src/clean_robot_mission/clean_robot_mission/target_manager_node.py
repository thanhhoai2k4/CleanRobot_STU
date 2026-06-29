import math

import rclpy

from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time

from std_msgs.msg import String

from geometry_msgs.msg import PoseStamped
from tf2_ros import (
    Buffer,
    ConnectivityException,
    ExtrapolationException,
    LookupException,
    TransformListener,
)

from clean_robot_msgs.msg import TrashCandidateArray


class TargetManagerNode(Node):

    def __init__(self):
        super().__init__('target_manager_node')

        self.declare_parameter(
            'candidate_topic',
            '/trash/tracked_candidates'
        )
        self.declare_parameter(
            'approach_distance_m',
            0.35
        )
        self.declare_parameter(
            'base_frame',
            'base_footprint'
        )

        self.approach_distance_m = max(
            0.0,
            float(self.get_parameter('approach_distance_m').value)
        )
        self.base_frame = self.get_parameter('base_frame').value
        self.rejected_targets = set()
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(
            self.tf_buffer,
            self
        )

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

        self.target_pose_pub.publish(
            self._approach_pose(best.pose)
        )

        self.get_logger().info(f'Selected target: {best.id}')

    def _approach_pose(self, trash_pose):
        frame_id = trash_pose.header.frame_id or 'map'

        try:
            base_tf = self.tf_buffer.lookup_transform(
                frame_id,
                self.base_frame,
                Time(),
                timeout=Duration(seconds=0.05)
            )
        except (
            LookupException,
            ConnectivityException,
            ExtrapolationException
        ) as exc:
            self.get_logger().warn(
                f'Cannot compute approach pose: {exc}',
                throttle_duration_sec=2.0
            )
            return self._fresh_pose(trash_pose)

        trash_x = trash_pose.pose.position.x
        trash_y = trash_pose.pose.position.y
        robot_x = base_tf.transform.translation.x
        robot_y = base_tf.transform.translation.y

        dx = trash_x - robot_x
        dy = trash_y - robot_y
        distance = math.hypot(dx, dy)
        if distance < 0.01 or self.approach_distance_m <= 0.0:
            return self._fresh_pose(trash_pose)

        standoff = min(
            self.approach_distance_m,
            max(0.0, distance - 0.05)
        )
        approach_x = trash_x - dx / distance * standoff
        approach_y = trash_y - dy / distance * standoff
        yaw = math.atan2(
            trash_y - approach_y,
            trash_x - approach_x
        )

        pose = PoseStamped()
        pose.header.frame_id = frame_id
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = approach_x
        pose.pose.position.y = approach_y
        pose.pose.position.z = 0.0
        pose.pose.orientation.z = math.sin(yaw * 0.5)
        pose.pose.orientation.w = math.cos(yaw * 0.5)
        return pose

    def _fresh_pose(self, pose):
        fresh = PoseStamped()
        fresh.header.frame_id = pose.header.frame_id or 'map'
        fresh.header.stamp = self.get_clock().now().to_msg()
        fresh.pose = pose.pose
        return fresh

def main(args=None):
    rclpy.init(args=args)
    node = TargetManagerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
