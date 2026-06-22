import rclpy

from rclpy.node import Node

from sensor_msgs.msg import Image

from clean_robot_msgs.msg import (
    TrashDetection2D,
    TrashDetection2DArray
)

from .yolo_model import YoloModel


class TrashDetectorNode(Node):

    def __init__(self):

        super().__init__(
            'trash_detector_node'
        )

        self.model = YoloModel()

        self.subscription = (
            self.create_subscription(
                Image,
                '/camera/image_raw',
                self.image_callback,
                10
            )
        )

        self.publisher = (
            self.create_publisher(
                TrashDetection2DArray,
                '/trash/detections',
                10
            )
        )

        self.get_logger().info(
            'TrashDetectorNode started'
        )

    def image_callback(self, image_msg):

        results = self.model.detect(
            image_msg
        )

        array_msg = (
            TrashDetection2DArray()
        )

        for result in results:

            det = TrashDetection2D()

            det.class_name = (
                result["class_name"]
            )

            det.confidence = (
                float(result["confidence"])
            )

            det.x = result["x"]

            det.y = result["y"]

            det.width = result["width"]

            det.height = result["height"]

            array_msg.detections.append(
                det
            )

        self.publisher.publish(
            array_msg
        )


def main(args=None):

    rclpy.init(args=args)

    node = TrashDetectorNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()