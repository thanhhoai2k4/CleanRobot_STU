from pathlib import Path

import rclpy

from rclpy.node import Node

from sensor_msgs.msg import Image

from clean_robot_msgs.msg import (
    TrashDetection2D,
    TrashDetection2DArray
)

from .yolo_model import YoloModel


def default_model_path():
    for parent in Path(__file__).resolve().parents:
        candidate = parent / 'best.pt'
        if candidate.is_file():
            return str(candidate)

    return 'best.pt'


class TrashDetectorNode(Node):

    def __init__(self):

        super().__init__(
            'trash_detector_node'
        )

        self.declare_parameter(
            'image_topic',
            '/camera/image_raw/image_color'
        )
        self.declare_parameter(
            'model_path',
            default_model_path()
        )
        self.declare_parameter(
            'confidence_threshold',
            0.35
        )
        self.declare_parameter(
            'target_classes',
            'chai_nhua,lon_nuoc'
        )

        target_classes = [
            item.strip()
            for item in self.get_parameter(
                'target_classes'
            ).value.split(',')
            if item.strip()
        ]

        self.model = YoloModel(
            model_path=self.get_parameter('model_path').value,
            confidence_threshold=float(
                self.get_parameter('confidence_threshold').value
            ),
            target_classes=target_classes
        )

        self.subscription = (
            self.create_subscription(
                Image,
                self.get_parameter('image_topic').value,
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
        array_msg.header = image_msg.header

        for result in results:

            det = TrashDetection2D()
            det.header = image_msg.header

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
