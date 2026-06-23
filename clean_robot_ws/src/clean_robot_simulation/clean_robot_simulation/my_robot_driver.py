import rclpy
from geometry_msgs.msg import Twist

# Bạn có thể tinh chỉnh các thông số này theo kích thước thật của robot trong Webots
HALF_DISTANCE_BETWEEN_WHEELS = 0.045
WHEEL_RADIUS = 0.025

class MyRobotDriver:
    def init(self, webots_node, properties):
        self.__robot = webots_node.robot

        # Tên động cơ phải KHỚP CHÍNH XÁC với tên Device trong file cấu hình my_world.wbt
        self.__left_motor = self.__robot.getDevice('left wheel motor')
        self.__right_motor = self.__robot.getDevice('right wheel motor')

        self.__left_motor.setPosition(float('inf'))
        self.__left_motor.setVelocity(0.0)

        self.__right_motor.setPosition(float('inf'))
        self.__right_motor.setVelocity(0.0)

        self.__target_twist = Twist()

        rclpy.init(args=None)
        self.__node = rclpy.create_node('my_robot_driver_node')
        # Lắng nghe topic /cmd_vel mà file clean_robot_simulation.py của bạn đang phát ra
        self.__node.create_subscription(Twist, '/cmd_vel', self.__cmd_vel_callback, 1)

    def __cmd_vel_callback(self, twist):
        self.__target_twist = twist

    def step(self):
        rclpy.spin_once(self.__node, timeout_sec=0)

        forward_speed = self.__target_twist.linear.x
        angular_speed = self.__target_twist.angular.z

        # Tính toán vận tốc cho từng bánh xe (Differential Drive kinematics)
        command_motor_left = (forward_speed - angular_speed * HALF_DISTANCE_BETWEEN_WHEELS) / WHEEL_RADIUS
        command_motor_right = (forward_speed + angular_speed * HALF_DISTANCE_BETWEEN_WHEELS) / WHEEL_RADIUS

        self.__left_motor.setVelocity(command_motor_left)
        self.__right_motor.setVelocity(command_motor_right)