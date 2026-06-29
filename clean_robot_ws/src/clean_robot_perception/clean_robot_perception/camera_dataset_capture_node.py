from datetime import datetime
from pathlib import Path

import cv2
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image

from .image_utils import ImageConversionError, ImageUtils


def default_output_dir():
    source_path = Path(__file__).resolve()

    for parent in source_path.parents:
        if (
            (parent / 'clean_robot_ws').is_dir()
            and (parent / 'AGENTS.md').is_file()
        ):
            return str(parent / 'dataset' / 'images')

    return 'dataset/images'


class CameraDatasetCaptureNode(Node):

    def __init__(self):
        super().__init__('camera_dataset_capture_node')

        self.declare_parameter(
            'image_topic',
            '/camera/image_raw/image_color'
        )
        self.declare_parameter(
            'output_dir',
            default_output_dir()
        )
        self.declare_parameter(
            'interval_sec',
            2.0
        )
        self.declare_parameter(
            'filename_prefix',
            'clean_robot'
        )
        self.declare_parameter(
            'image_format',
            'jpg'
        )
        self.declare_parameter(
            'jpeg_quality',
            95
        )

        self.image_topic = self.get_parameter('image_topic').value
        self.output_dir = Path(
            str(self.get_parameter('output_dir').value)
        ).expanduser()
        self.interval_sec = max(
            0.1,
            float(self.get_parameter('interval_sec').value)
        )
        self.filename_prefix = str(
            self.get_parameter('filename_prefix').value
        )
        self.image_format = str(
            self.get_parameter('image_format').value
        ).lower().lstrip('.')
        self.jpeg_quality = int(
            self.get_parameter('jpeg_quality').value
        )

        if self.image_format == 'jpeg':
            self.image_format = 'jpg'

        if self.image_format not in {'jpg', 'png'}:
            self.get_logger().warning(
                f'Unsupported image_format="{self.image_format}", using jpg.'
            )
            self.image_format = 'jpg'

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.latest_image_msg = None
        self.has_new_image = False
        self.saved_count = 0
        self.wait_log_count = 0

        self.create_subscription(
            Image,
            self.image_topic,
            self.image_callback,
            qos_profile_sensor_data
        )
        self.create_timer(
            self.interval_sec,
            self.capture_timer_callback
        )

        self.get_logger().info(
            'CameraDatasetCaptureNode started: '
            f'topic={self.image_topic}, '
            f'output_dir={self.output_dir}, '
            f'interval_sec={self.interval_sec}'
        )

    def image_callback(self, image_msg):
        self.latest_image_msg = image_msg
        self.has_new_image = True

    def capture_timer_callback(self):
        if self.latest_image_msg is None:
            self.wait_log_count += 1
            if self.wait_log_count == 1 or self.wait_log_count % 10 == 0:
                self.get_logger().warning(
                    f'Waiting for images on {self.image_topic}'
                )
            return

        if not self.has_new_image:
            return

        try:
            frame = ImageUtils.to_bgr8(self.latest_image_msg)
        except ImageConversionError as exc:
            self.get_logger().error(
                f'Failed to convert image: {exc}'
            )
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        filename = (
            f'{self.filename_prefix}_{timestamp}_'
            f'{self.saved_count:06d}.{self.image_format}'
        )
        output_path = self.output_dir / filename

        params = []
        if self.image_format == 'jpg':
            params = [
                cv2.IMWRITE_JPEG_QUALITY,
                max(0, min(100, self.jpeg_quality))
            ]

        saved = cv2.imwrite(
            str(output_path),
            frame,
            params
        )

        if not saved:
            self.get_logger().error(
                f'Failed to write image: {output_path}'
            )
            return

        self.has_new_image = False
        self.saved_count += 1

        if self.saved_count == 1 or self.saved_count % 10 == 0:
            self.get_logger().info(
                f'Saved {self.saved_count} image(s). '
                f'Latest: {output_path}'
            )


def main(args=None):
    rclpy.init(args=args)

    node = CameraDatasetCaptureNode()

    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
