import rclpy
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from rclpy.time import Time
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster
import math

# Thông số vật lý robot - phải khớp với Webots world
HALF_DISTANCE_BETWEEN_WHEELS = 0.045  # nửa khoảng cách giữa 2 bánh (mét)
WHEEL_RADIUS = 0.025                   # bán kính bánh xe (mét)


def normalize_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


class MyRobotDriver:
    def init(self, webots_node, properties):
        self.__robot = webots_node.robot
        if not rclpy.ok():
            rclpy.init(args=None)
        self.__node = rclpy.create_node('my_robot_driver_node')

        # ── Bước 2: Lấy thiết bị động cơ từ Webots ─────────────────────────
        self.__left_motor = self.__robot.getDevice('left wheel motor')
        self.__right_motor = self.__robot.getDevice('right wheel motor')
        self.__left_motor.setPosition(float('inf'))
        self.__left_motor.setVelocity(0.0)
        self.__right_motor.setPosition(float('inf'))
        self.__right_motor.setVelocity(0.0)

        # ── Bước 3: Lấy encoder vị trí (PositionSensor) ────────────────────
        timestep = int(self.__robot.getBasicTimeStep())
        self.__left_pos_sensor = self.__robot.getDevice('left wheel sensor')
        self.__right_pos_sensor = self.__robot.getDevice('right wheel sensor')
        if self.__left_pos_sensor is not None:
            self.__left_pos_sensor.enable(timestep)
        if self.__right_pos_sensor is not None:
            self.__right_pos_sensor.enable(timestep)
        self.__has_encoders = (self.__left_pos_sensor is not None and
                               self.__right_pos_sensor is not None)

        # Ground-truth pose từ Webots giúp SLAM trong mô phỏng ổn định hơn
        # encoder khi bánh bị trượt hoặc mô hình vật lý chưa khớp tuyệt đối.
        self.__gps = self.__robot.getDevice('gps')
        self.__imu = self.__robot.getDevice('inertial_unit')
        if self.__gps is not None:
            self.__gps.enable(timestep)
        if self.__imu is not None:
            self.__imu.enable(timestep)
        self.__has_ground_truth_pose = self.__gps is not None and self.__imu is not None

        # ── Bước 4: Đăng ký subscriber và publishers ───────────────────────
        self.__target_twist = Twist()
        self.__node.create_subscription(Twist, '/cmd_vel', self.__cmd_vel_callback, 1)
        self.__odom_pub = self.__node.create_publisher(Odometry, '/odom', 10)
        self.__joint_state_pub = self.__node.create_publisher(JointState, '/joint_states', 10)
        self.__tf_broadcaster = TransformBroadcaster(self.__node)

        # ── Bước 5: Khởi tạo biến trạng thái ──────────────────────────────
        self.x = 0.0
        self.y = 0.0
        self.th = 0.0
        self.last_time = self.__robot.getTime()
        self.__last_left_pos = 0.0
        self.__last_right_pos = 0.0
        self.__encoders_initialized = False
        # Tích lũy vị trí joint để publish joint_states khi không có encoder
        self.__joint_left_pos = 0.0
        self.__joint_right_pos = 0.0
        self.__initial_gt_x = 0.0
        self.__initial_gt_y = 0.0
        self.__initial_gt_yaw = 0.0
        self.__ground_truth_initialized = False

        self.__node.get_logger().info(
            f'MyRobotDriver khởi tạo OK. Encoder: {"CÓ" if self.__has_encoders else "KHÔNG"}, '
            f'Ground truth odom: {"CÓ" if self.__has_ground_truth_pose else "KHÔNG"}'
        )

    def __cmd_vel_callback(self, twist):
        self.__target_twist = twist

    def step(self):
        try:
            rclpy.spin_once(self.__node, timeout_sec=0)
        except Exception:
            return

        forward_speed = self.__target_twist.linear.x
        angular_speed = self.__target_twist.angular.z

        # ── Điều khiển động cơ ────────────────────────────────────────────
        cmd_left  = (forward_speed - angular_speed * HALF_DISTANCE_BETWEEN_WHEELS) / WHEEL_RADIUS
        cmd_right = (forward_speed + angular_speed * HALF_DISTANCE_BETWEEN_WHEELS) / WHEEL_RADIUS
        self.__left_motor.setVelocity(cmd_left)
        self.__right_motor.setVelocity(cmd_right)

        # ── Lấy thời gian hiện tại ───────────────────────────────────────
        current_time = self.__robot.getTime()
        current_stamp = Time(seconds=current_time).to_msg()
        dt = current_time - self.last_time
        if dt <= 0.0:
            return

        linear_twist = forward_speed
        angular_twist = angular_speed

        # ── Đọc encoder để publish joint_states ───────────────────────────
        encoder_linear_delta = 0.0
        encoder_angular_delta = 0.0
        if self.__has_encoders:
            left_pos  = self.__left_pos_sensor.getValue()
            right_pos = self.__right_pos_sensor.getValue()

            if not self.__encoders_initialized:
                self.__last_left_pos  = left_pos
                self.__last_right_pos = right_pos
                self.__encoders_initialized = True
            else:
                delta_left  = left_pos  - self.__last_left_pos
                delta_right = right_pos - self.__last_right_pos
                self.__last_left_pos  = left_pos
                self.__last_right_pos = right_pos

                dist_left  = delta_left  * WHEEL_RADIUS
                dist_right = delta_right * WHEEL_RADIUS
                encoder_linear_delta = (dist_right + dist_left) / 2.0
                encoder_angular_delta = (dist_right - dist_left) / (2.0 * HALF_DISTANCE_BETWEEN_WHEELS)

                linear_twist = encoder_linear_delta / dt
                angular_twist = encoder_angular_delta / dt

            self.__joint_left_pos  = left_pos
            self.__joint_right_pos = right_pos
        else:
            self.__joint_left_pos  += cmd_left * dt
            self.__joint_right_pos += cmd_right * dt

        # ── Tính Odometry ─────────────────────────────────────────────────
        if self.__has_ground_truth_pose:
            gps_values = self.__gps.getValues()
            yaw = self.__imu.getRollPitchYaw()[2]

            if not self.__ground_truth_initialized:
                self.__initial_gt_x = gps_values[0]
                self.__initial_gt_y = gps_values[1]
                self.__initial_gt_yaw = yaw
                self.__ground_truth_initialized = True

            world_dx = gps_values[0] - self.__initial_gt_x
            world_dy = gps_values[1] - self.__initial_gt_y
            cos_yaw0 = math.cos(-self.__initial_gt_yaw)
            sin_yaw0 = math.sin(-self.__initial_gt_yaw)

            next_x = cos_yaw0 * world_dx - sin_yaw0 * world_dy
            next_y = sin_yaw0 * world_dx + cos_yaw0 * world_dy
            next_th = normalize_angle(yaw - self.__initial_gt_yaw)

            dx = next_x - self.x
            dy = next_y - self.y
            dth = normalize_angle(next_th - self.th)
            linear_twist = (dx * math.cos(self.th) + dy * math.sin(self.th)) / dt
            angular_twist = dth / dt

            self.x = next_x
            self.y = next_y
            self.th = next_th
        elif self.__has_encoders:
            self.x += encoder_linear_delta * math.cos(self.th)
            self.y += encoder_linear_delta * math.sin(self.th)
            self.th = normalize_angle(self.th + encoder_angular_delta)
        else:
            self.x += forward_speed * math.cos(self.th) * dt
            self.y += forward_speed * math.sin(self.th) * dt
            self.th = normalize_angle(self.th + angular_speed * dt)
        self.last_time = current_time

        # ── Publish /joint_states ──────────────────────────────────────────
        # robot_state_publisher CẦN topic này để tạo TF cho lidar_link, camera_link, v.v.
        joint_state = JointState()
        joint_state.header.stamp = current_stamp
        joint_state.name = ['left_wheel_joint', 'right_wheel_joint']
        joint_state.position = [float(self.__joint_left_pos), float(self.__joint_right_pos)]
        self.__joint_state_pub.publish(joint_state)

        # ── Publish TF: odom → base_footprint ────────────────────────────
        t = TransformStamped()
        t.header.stamp = current_stamp
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_footprint'
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        t.transform.rotation.z = math.sin(self.th / 2.0)
        t.transform.rotation.w = math.cos(self.th / 2.0)
        self.__tf_broadcaster.sendTransform(t)

        # ── Publish /odom message ─────────────────────────────────────────
        odom = Odometry()
        odom.header.stamp = current_stamp
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_footprint'
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.orientation = t.transform.rotation
        
        odom.twist.twist.linear.x = linear_twist
        odom.twist.twist.angular.z = angular_twist
        
        self.__odom_pub.publish(odom)
