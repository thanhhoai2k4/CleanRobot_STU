from action_msgs.msg import GoalStatus
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient


class Nav2Client:

    IDLE = 'IDLE'
    SENDING = 'SENDING'
    ACTIVE = 'ACTIVE'
    SUCCEEDED = 'SUCCEEDED'
    FAILED = 'FAILED'
    REJECTED = 'REJECTED'
    CANCELED = 'CANCELED'

    def __init__(self, node):
        self.node = node
        self._client = ActionClient(
            node,
            NavigateToPose,
            'navigate_to_pose'
        )
        self._goal_handle = None
        self._status = self.IDLE

    def send_goal(self, pose):
        if self._status in (self.SENDING, self.ACTIVE):
            return True

        if not self._client.wait_for_server(timeout_sec=0.1):
            self.node.get_logger().warn(
                'Nav2 action server navigate_to_pose is not ready',
                throttle_duration_sec=2.0
            )
            return False

        goal = NavigateToPose.Goal()
        goal.pose = pose
        self._status = self.SENDING

        self.node.get_logger().info(
            f'Sending Nav2 goal: x={pose.pose.position.x:.2f}, '
            f'y={pose.pose.position.y:.2f}'
        )
        future = self._client.send_goal_async(goal)
        future.add_done_callback(self._goal_response_callback)
        return True

    def get_status(self):
        return self._status

    def reset(self):
        self._goal_handle = None
        self._status = self.IDLE

    def cancel_goal(self):
        if self._goal_handle is None:
            self.reset()
            return

        self._goal_handle.cancel_goal_async()
        self._status = self.CANCELED

    def _goal_response_callback(self, future):
        self._goal_handle = future.result()
        if not self._goal_handle.accepted:
            self.node.get_logger().warn('Nav2 goal was rejected')
            self._status = self.REJECTED
            return

        self.node.get_logger().info('Nav2 goal accepted')
        self._status = self.ACTIVE
        result_future = self._goal_handle.get_result_async()
        result_future.add_done_callback(self._result_callback)

    def _result_callback(self, future):
        result = future.result()

        if result.status == GoalStatus.STATUS_SUCCEEDED:
            self._status = self.SUCCEEDED
            self.node.get_logger().info('Nav2 goal succeeded')
            return

        if result.status == GoalStatus.STATUS_CANCELED:
            self._status = self.CANCELED
            self.node.get_logger().warn('Nav2 goal canceled')
            return

        self._status = self.FAILED
        self.node.get_logger().warn(
            f'Nav2 goal failed with status {result.status}'
        )
