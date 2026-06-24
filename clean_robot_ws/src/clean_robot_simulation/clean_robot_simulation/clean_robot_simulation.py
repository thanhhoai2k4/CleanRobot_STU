import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from dataclasses import dataclass



#              Z+
#              ↑
#              |
#              |        angular.z
#              |       ↺ quay trái
#              |       ↻ quay phải
#              |
#              |
#   Y+  ←------ robot ------→  Y-
#              |
#              |
#              ↓
#              X-
           
#   X+ là hướng robot tiến tới
# y: dùng để dịch chuyển sang trái.
# Thông thường xe không thể tự dịch sang trai hay phải mà phải: quay 1 góc sang trái(z) rồi mới tăng x. :V


# CASE:
# FORWARD:
#   linear.x = +1 # không sử dụng += vì đây đang là vận tốc (velocity)
#   linear.y = 0
#   linear.z = 0
#
# BACKWARD:
#   linear.x = -1
#   linear.y = 0
#   linear.z = 0
#
# LEFT:
#   linear.x = 0
#   linear.y = 0
#   linear.z = +1 
#
#
# RIGHT:
#   linear.x = 0
#   linear.y = 0
#   linear.z = -1 
#
# STOP:
#   0,0,0 :V
#
# linear.x = +1 . 1 ở đây là ví dụ


# /cmd_vel
class ManualCmdNode(Node):
    def __init__(self):
        super().__init__('manual_cmd_node') # name node
        self.declare_parameter('linear_speed', 0.15) # this is ros2'declare
        self.declare_parameter('angular_speed', 0.8) # this is ros2'declare

        self.linear_speed = float(self.get_parameter('linear_speed').value)
        self.angular_speed = float(self.get_parameter('angular_speed').value)


        self.cmd_sub = self.create_subscription(
            String, # Type response
            '/robot/manual_cmd', # name_node publish into ManualCmdNode
            self.manual_cmd_callback,
            10 # size cache: if size overload, we keep 10 data line
        ) # Subscriber: other -> response type: string (from std.msgs import String) -> ManualCmdNode

        self.velocity_publisher = self.create_publisher(
            Twist, '/cmd_vel', 10)
        self.get_logger().info("ManualCmdNode: clean_robot_simulation")

    def manual_cmd_callback(self, msg: String):
        """
            msg{
                "data": string
            }
        """

        # u->U
        command = msg.data.strip().upper()

        twist = Twist()

        if command == 'FORWARD':
            twist.linear.x = self.linear_speed
            twist.angular.z = 0.0
            self.get_logger().info("Command received: FORWARD")
        elif command == "BACKWARD":
            twist.linear.x = -self.linear_speed
            twist.angular.z = 0.0
            self.get_logger().info("Command received: BACKWARD")
        elif command == "LEFT":
            twist.linear.x = 0.0
            twist.angular.z = self.angular_speed
            self.get_logger().info("Command received: LEFT")
        elif command == "RIGHT":
            twist.linear.x = 0.0
            twist.angular.z = -self.angular_speed
            self.get_logger().info("Command received: RIGHT")
        elif command == "STOP":
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.get_logger().info("Command received: STOP")
        else:
            self.get_logger().warn(f"Invalid command: {command}")
            return

        try:
            self.velocity_publisher.publish(twist) # send data to /cmd_vel
        except Exception as e:
            self.get_logger().info(f"Nhận được lỗi: {e}")
    def stop_robot(self):
        twist = Twist()
        try:
            self.velocity_publisher.publish(twist)
        except Exception:
            pass

def main(args=None):
    rclpy.init(args=args)
    node = ManualCmdNode()
    try:
        rclpy.spin(node) # while true: node.run()... Keep it long living
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()
        try:
            node.destroy_node()
        except (Exception, KeyboardInterrupt):
            pass
        try:
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()
