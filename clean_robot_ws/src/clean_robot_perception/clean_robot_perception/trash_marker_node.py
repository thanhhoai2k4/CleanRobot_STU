import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray

from clean_robot_msgs.msg import TrashCandidateArray


class TrashMarkerNode(Node):

    def __init__(self):
        super().__init__('trash_marker_node')

        self.declare_parameter(
            'candidate_topic',
            '/trash/tracked_candidates'
        )
        self.declare_parameter(
            'marker_topic',
            '/trash/markers'
        )

        self.subscription = self.create_subscription(
            TrashCandidateArray,
            self.get_parameter('candidate_topic').value,
            self.callback,
            10
        )
        self.publisher = self.create_publisher(
            MarkerArray,
            self.get_parameter('marker_topic').value,
            10
        )

        self.get_logger().info('TrashMarkerNode started')

    def callback(self, msg):
        marker_array = MarkerArray()

        clear_marker = Marker()
        clear_marker.action = Marker.DELETEALL
        marker_array.markers.append(clear_marker)

        for index, candidate in enumerate(msg.candidates):
            pose = candidate.pose.pose
            header = candidate.pose.header
            if not header.frame_id:
                header.frame_id = msg.header.frame_id or 'map'

            marker_array.markers.append(
                self._object_marker(index, header, pose, candidate)
            )
            marker_array.markers.append(
                self._text_marker(index, header, pose, candidate)
            )

        self.publisher.publish(marker_array)

    def _object_marker(self, index, header, pose, candidate):
        marker = Marker()
        marker.header = header
        marker.ns = 'trash_objects'
        marker.id = index * 2
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        marker.pose.position.x = pose.position.x
        marker.pose.position.y = pose.position.y
        marker.pose.position.z = max(0.05, pose.position.z)
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.14
        marker.scale.y = 0.14
        marker.scale.z = 0.14
        marker.color.a = 0.95
        marker.color.r = 1.0
        marker.color.g = 0.25 if candidate.reachable else 0.0
        marker.color.b = 0.05
        return marker

    def _text_marker(self, index, header, pose, candidate):
        marker = Marker()
        marker.header = header
        marker.ns = 'trash_labels'
        marker.id = index * 2 + 1
        marker.type = Marker.TEXT_VIEW_FACING
        marker.action = Marker.ADD
        marker.pose.position.x = pose.position.x
        marker.pose.position.y = pose.position.y
        marker.pose.position.z = max(0.22, pose.position.z + 0.22)
        marker.pose.orientation.w = 1.0
        marker.scale.z = 0.12
        marker.color.a = 1.0
        marker.color.r = 1.0
        marker.color.g = 1.0
        marker.color.b = 1.0
        marker.text = (
            f'{candidate.id} | {candidate.class_name}\n'
            f'conf={candidate.confidence:.2f} '
            f'x={pose.position.x:.2f} y={pose.position.y:.2f}'
        )
        return marker


def main(args=None):
    rclpy.init(args=args)
    node = TrashMarkerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
