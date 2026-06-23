import rclpy

from rclpy.node import Node

from clean_robot_msgs.msg import (
    TrashCandidate,
    TrashCandidateArray
)


class FakeTrashCandidateNode(Node):

    def __init__(self):

        super().__init__(
            'fake_trash_candidate_node'
        )

        self.pub = self.create_publisher(
            TrashCandidateArray,
            '/trash/candidates',
            10
        )

        self.timer = self.create_timer(
            5.0,
            self.publish_fake_target
        )

        self.counter = 0

    def publish_fake_target(self):

        candidate = TrashCandidate()

        candidate.id = (
            f'trash_{self.counter}'
        )

        candidate.class_name = 'bottle'

        candidate.confidence = 0.95

        candidate.reachable = True

        candidate.status = 'NEW'

        candidate.pose.header.frame_id = 'map'

        candidate.pose.pose.position.x = 2.0

        candidate.pose.pose.position.y = 1.0

        msg = TrashCandidateArray()

        msg.candidates.append(
            candidate
        )

        self.pub.publish(msg)

        self.counter += 1

        self.get_logger().info(
            'Fake target published'
        )


def main(args=None):

    rclpy.init(args=args)

    node = FakeTrashCandidateNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()