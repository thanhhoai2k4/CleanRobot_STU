#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import LaserScan


class ScanNormalizerNode(Node):
    def __init__(self):
        super().__init__('scan_normalizer_node')
        self.declare_parameter('input_topic', '/scan')
        self.declare_parameter('output_topic', '/scan_normalized')

        input_topic = self.get_parameter('input_topic').get_parameter_value().string_value
        output_topic = self.get_parameter('output_topic').get_parameter_value().string_value

        scan_subscription_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
        )
        scan_publisher_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
        )

        self.publisher = self.create_publisher(LaserScan, output_topic, scan_publisher_qos)
        self.subscription = self.create_subscription(
            LaserScan,
            input_topic,
            self.scan_callback,
            scan_subscription_qos,
        )

        self.get_logger().info(f'Normalizing LaserScan {input_topic} -> {output_topic}')

    def scan_callback(self, msg):
        if msg.angle_increment >= 0.0 and msg.angle_min <= msg.angle_max:
            self.publisher.publish(msg)
            return

        normalized = LaserScan()
        normalized.header = msg.header
        normalized.angle_min = msg.angle_max
        normalized.angle_max = msg.angle_min
        normalized.angle_increment = abs(msg.angle_increment)
        normalized.time_increment = msg.time_increment
        normalized.scan_time = msg.scan_time
        normalized.range_min = msg.range_min
        normalized.range_max = msg.range_max
        normalized.ranges = list(reversed(msg.ranges))
        if len(msg.intensities) == len(msg.ranges):
            normalized.intensities = list(reversed(msg.intensities))
        else:
            normalized.intensities = list(msg.intensities)

        self.publisher.publish(normalized)


def main(args=None):
    rclpy.init(args=args)
    node = ScanNormalizerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        try:
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()
