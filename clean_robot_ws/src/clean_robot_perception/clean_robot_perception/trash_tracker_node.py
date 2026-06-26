import rclpy

from rclpy.node import Node

from clean_robot_msgs.msg import (
    TrashCandidateArray
)


class TrashTrackerNode(Node):

    def __init__(self):

        super().__init__(
            'trash_tracker_node'
        )

        self.declare_parameter(
            'min_observations',
            3
        )
        self.min_observations = max(
            1,
            int(self.get_parameter('min_observations').value)
        )

        self.subscription = (
            self.create_subscription(
                TrashCandidateArray,
                '/trash/candidates',
                self.callback,
                10
            )
        )

        self.publisher = (
            self.create_publisher(
                TrashCandidateArray,
                '/trash/tracked_candidates',
                10
            )
        )

        self.counter = {}
        self.get_logger().info(
            'TrashTrackerNode started'
        )

    def callback(self, msg):

        filtered = (
            TrashCandidateArray()
        )
        filtered.header = msg.header

        for candidate in msg.candidates:

            key = (
                candidate.id
            )

            self.counter[key] = (
                self.counter.get(key, 0)
                + 1
            )

            if self.counter[key] >= self.min_observations:

                filtered.candidates.append(
                    candidate
                )

        self.publisher.publish(
            filtered
        )


def main(args=None):

    rclpy.init(args=args)

    node = TrashTrackerNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
