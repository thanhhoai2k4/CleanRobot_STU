import math

import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from sensor_msgs.msg import Image
from tf2_ros import (
    Buffer,
    ConnectivityException,
    ExtrapolationException,
    LookupException,
    TransformListener,
)

from clean_robot_msgs.msg import (
    TrashCandidate,
    TrashCandidateArray,
    TrashDetection2DArray,
)


class TrashLocalizationNode(Node):

    def __init__(self):

        super().__init__(
            'trash_localization_node'
        )

        self.declare_parameter(
            'depth_topic',
            '/depth_camera/image_depth/image'
        )
        self.declare_parameter(
            'target_frame',
            'map'
        )
        self.declare_parameter(
            'camera_frame',
            'camera_link'
        )
        self.declare_parameter(
            'rgb_image_width',
            640
        )
        self.declare_parameter(
            'rgb_image_height',
            480
        )
        self.declare_parameter(
            'horizontal_fov',
            1.0472
        )
        self.declare_parameter(
            'depth_scale',
            1.0
        )
        self.declare_parameter(
            'min_depth_m',
            0.05
        )
        self.declare_parameter(
            'max_depth_m',
            3.0
        )
        self.declare_parameter(
            'depth_sample_window',
            5
        )
        self.declare_parameter(
            'id_grid_m',
            0.25
        )

        self.target_frame = self.get_parameter(
            'target_frame'
        ).value
        self.camera_frame = self.get_parameter(
            'camera_frame'
        ).value
        self.rgb_image_width = int(
            self.get_parameter('rgb_image_width').value
        )
        self.rgb_image_height = int(
            self.get_parameter('rgb_image_height').value
        )
        self.horizontal_fov = float(
            self.get_parameter('horizontal_fov').value
        )
        self.depth_scale = float(
            self.get_parameter('depth_scale').value
        )
        self.min_depth_m = float(
            self.get_parameter('min_depth_m').value
        )
        self.max_depth_m = float(
            self.get_parameter('max_depth_m').value
        )
        self.depth_sample_window = max(
            1,
            int(self.get_parameter('depth_sample_window').value)
        )
        self.id_grid_m = max(
            0.01,
            float(self.get_parameter('id_grid_m').value)
        )

        self.bridge = CvBridge()
        self.latest_depth = None
        self.latest_depth_stamp = None
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(
            self.tf_buffer,
            self
        )

        self.depth_subscription = (
            self.create_subscription(
                Image,
                self.get_parameter('depth_topic').value,
                self.depth_callback,
                10
            )
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

        self.get_logger().info(
            'TrashLocalizationNode started'
        )

    def depth_callback(self, msg):
        try:
            depth = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='passthrough'
            )
        except Exception as exc:
            self.get_logger().warn(
                f'Cannot convert depth image: {exc}',
                throttle_duration_sec=2.0
            )
            return

        self.latest_depth = np.asarray(depth)
        self.latest_depth_stamp = msg.header.stamp

    def callback(self, msg):

        output = TrashCandidateArray()
        output.header = msg.header

        if self.latest_depth is None:
            self.get_logger().warn(
                'No depth image received yet, cannot localize trash',
                throttle_duration_sec=2.0
            )
            self.publisher.publish(output)
            return

        for detection in msg.detections:
            point_camera = self._point_from_detection(detection)
            if point_camera is None:
                continue

            source_frame = (
                detection.header.frame_id
                or msg.header.frame_id
                or self.camera_frame
            )
            point_map = self._transform_point(
                point_camera,
                source_frame
            )
            if point_map is None:
                continue

            candidate = TrashCandidate()
            candidate.header = msg.header
            candidate.header.frame_id = self.target_frame

            candidate.id = (
                self._candidate_id(
                    detection.class_name,
                    point_map[0],
                    point_map[1]
                )
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
                self.target_frame
            )
            candidate.pose.header.stamp = msg.header.stamp

            candidate.pose.pose.position.x = (
                point_map[0]
            )

            candidate.pose.pose.position.y = (
                point_map[1]
            )
            candidate.pose.pose.position.z = (
                point_map[2]
            )
            candidate.pose.pose.orientation.w = 1.0

            output.candidates.append(
                candidate
            )

        self.publisher.publish(output)

    def _point_from_detection(self, detection):
        depth = self.latest_depth
        if depth.ndim == 3:
            depth = depth[:, :, 0]

        depth_height, depth_width = depth.shape[:2]
        rgb_width = max(1, self.rgb_image_width)
        rgb_height = max(1, self.rgb_image_height)

        center_u_rgb = detection.x + detection.width * 0.5
        center_v_rgb = detection.y + detection.height * 0.5
        center_u = int(round(center_u_rgb * depth_width / rgb_width))
        center_v = int(round(center_v_rgb * depth_height / rgb_height))
        center_u = min(max(center_u, 0), depth_width - 1)
        center_v = min(max(center_v, 0), depth_height - 1)

        distance = self._sample_depth(
            depth,
            center_u,
            center_v
        )
        if distance is None:
            return None

        fx = depth_width / (
            2.0 * math.tan(self.horizontal_fov / 2.0)
        )
        fy = fx
        cx = (depth_width - 1) / 2.0
        cy = (depth_height - 1) / 2.0

        right = (center_u - cx) * distance / fx
        down = (center_v - cy) * distance / fy

        # camera_link in this robot is modeled as x-forward, y-left, z-up.
        return (
            distance,
            -right,
            -down
        )

    def _sample_depth(self, depth, center_u, center_v):
        radius = self.depth_sample_window // 2
        min_u = max(0, center_u - radius)
        max_u = min(depth.shape[1], center_u + radius + 1)
        min_v = max(0, center_v - radius)
        max_v = min(depth.shape[0], center_v + radius + 1)

        window = depth[min_v:max_v, min_u:max_u].astype(float)
        values = window[np.isfinite(window) & (window > 0.0)]
        if values.size == 0:
            return None

        distance = float(np.median(values)) * self.depth_scale
        if (
            distance < self.min_depth_m
            or distance > self.max_depth_m
        ):
            return None

        return distance

    def _transform_point(self, point, source_frame):
        try:
            transform = self.tf_buffer.lookup_transform(
                self.target_frame,
                source_frame,
                Time(),
                timeout=Duration(seconds=0.1)
            )
        except (
            LookupException,
            ConnectivityException,
            ExtrapolationException
        ) as exc:
            self.get_logger().warn(
                f'Cannot transform {source_frame} -> '
                f'{self.target_frame}: {exc}',
                throttle_duration_sec=2.0
            )
            return None

        rotated = self._rotate_vector(
            transform.transform.rotation,
            point
        )
        translation = transform.transform.translation
        return (
            translation.x + rotated[0],
            translation.y + rotated[1],
            translation.z + rotated[2],
        )

    @staticmethod
    def _rotate_vector(quaternion, vector):
        qx = quaternion.x
        qy = quaternion.y
        qz = quaternion.z
        qw = quaternion.w
        vx, vy, vz = vector

        uv = (
            qy * vz - qz * vy,
            qz * vx - qx * vz,
            qx * vy - qy * vx,
        )
        uuv = (
            qy * uv[2] - qz * uv[1],
            qz * uv[0] - qx * uv[2],
            qx * uv[1] - qy * uv[0],
        )

        return (
            vx + 2.0 * (qw * uv[0] + uuv[0]),
            vy + 2.0 * (qw * uv[1] + uuv[1]),
            vz + 2.0 * (qw * uv[2] + uuv[2]),
        )

    def _candidate_id(self, class_name, x, y):
        clean_name = ''.join(
            char if char.isalnum() else '_'
            for char in class_name.lower()
        ).strip('_') or 'trash'
        grid_x = int(round(x / self.id_grid_m))
        grid_y = int(round(y / self.id_grid_m))
        return f'{clean_name}_{grid_x}_{grid_y}'


def main(args=None):

    rclpy.init(args=args)

    node = TrashLocalizationNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
