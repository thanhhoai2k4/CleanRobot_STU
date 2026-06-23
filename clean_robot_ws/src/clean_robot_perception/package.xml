import rclpy

from rclpy.node import Node

from clean_robot_msgs.msg import (
    TrashDetection2DArray,
    TrashCandidate,
    TrashCandidateArray
)


class TrashLocalizationNode(Node):

    def __init__(self):

        super().__init__(
            'trash_localization_node'
        )

        self.subscription = (
            self.create_subscription(
                TrashDetection2DArray,
                '/trash/detections',
                self.callback,
                10
            )
        )

        self.publisher = (
            self.create_publisher(
                TrashCandidateArray,
                '/trash/candidates',
                10
            )
        )

        self.counter = 0

    def callback(self, msg):

        output = TrashCandidateArray()

        for detection in msg.detections:

            candidate = TrashCandidate()

            candidate.id = (
                f'trash_{self.counter}'
            )

            candidate.class_name = (
                detection.class_name
            )

            candidate.confidence = (
                detection.confidence
            )

            candidate.reachable = True

            candidate.status = "NEW"

            candidate.pose.header.frame_id = (
                'map'
            )

            candidate.pose.pose.position.x = (
                2.0
            )

            candidate.pose.pose.position.y = (
                1.0
            )

            output.candidates.append(
                candidate
            )

            self.counter += 1

        self.publisher.publish(output)


def main(args=None):

    rclpy.init(args=args)

    node = TrashLocalizationNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()