# TÀI LIỆU DỰ ÁN CLEAN ROBOT

Cập nhật: 2026-06-26  
Workspace được khảo sát: `CleanRobot_STU/clean_robot_ws`

Tài liệu này mô tả hiện trạng source code đang có trong workspace. Những phần chưa thấy trong code được ghi rõ là **Chưa hoàn thiện**, **Đang thiết kế** hoặc **Cần bổ sung**. Không nên xem các phần đó là chức năng đã chạy ổn.

## Mục Lục

1. [Tổng quan dự án](#1-tổng-quan-dự-án)
2. [Kiến trúc tổng thể](#2-kiến-trúc-tổng-thể)
3. [Cấu trúc thư mục dự án](#3-cấu-trúc-thư-mục-dự-án)
4. [Giải thích từng package](#4-giải-thích-từng-package)
5. [Các topic ROS2 quan trọng](#5-các-topic-ros2-quan-trọng)
6. [Hướng dẫn cài đặt môi trường](#6-hướng-dẫn-cài-đặt-môi-trường)
7. [Hướng dẫn build dự án](#7-hướng-dẫn-build-dự-án)
8. [Hướng dẫn chạy mô phỏng Webots](#8-hướng-dẫn-chạy-mô-phỏng-webots)
9. [Hướng dẫn điều khiển robot](#9-hướng-dẫn-điều-khiển-robot)
10. [Giải thích Webots driver](#10-giải-thích-webots-driver)
11. [Hướng dẫn kiểm tra sensor](#11-hướng-dẫn-kiểm-tra-sensor)
12. [Hướng dẫn RViz](#12-hướng-dẫn-rviz)
13. [Hướng dẫn SLAM](#13-hướng-dẫn-slam)
14. [Hướng dẫn Nav2](#14-hướng-dẫn-nav2)
15. [Debug lỗi thường gặp](#15-debug-lỗi-thường-gặp)
16. [Quy trình làm việc cho thành viên mới](#16-quy-trình-làm-việc-cho-thành-viên-mới)
17. [Phân công module](#17-phân-công-module)
18. [Chuẩn đặt tên topic/frame](#18-chuẩn-đặt-tên-topicframe)
19. [Lộ trình phát triển tiếp theo](#19-lộ-trình-phát-triển-tiếp-theo)
20. [Phụ lục lệnh ROS2 thường dùng](#20-phụ-lục-lệnh-ros2-thường-dùng)
21. [Kết luận](#21-kết-luận)

---

## 1. Tổng quan dự án

### Clean Robot là gì?

Clean Robot là dự án robot nhặt rác mô phỏng bằng Webots và điều khiển bằng ROS2. Robot hiện được mô phỏng như một robot hai bánh kiểu differential drive, có camera RGB, depth camera/range finder, LiDAR, GPS, IMU và encoder bánh xe trong Webots.

### Mục tiêu hiện tại

Mục tiêu hiện tại của dự án là xây dựng nền tảng mô phỏng ổn định:

- Robot chạy được trong Webots.
- ROS2 điều khiển robot qua `/cmd_vel`.
- Robot publish được `/odom`, `/tf`, `/joint_states`.
- Webots publish sensor như `/scan`, camera RGB, depth camera và `/clock`.
- Chuẩn bị pipeline perception để phát hiện rác.
- Chuẩn bị SLAM/Nav2 để robot tự lập bản đồ và đi tới mục tiêu.
- Chuẩn bị mission manager để nhận mục tiêu rác và gửi goal cho Nav2.

### Dự án đang ở giai đoạn nào?

Dự án đang ở giai đoạn **mô phỏng + tích hợp nền tảng**. Các package chính đã tồn tại và đã có code cho simulation, message, perception, mission, navigation. Tuy nhiên một số phần vẫn cần kiểm thử tích hợp đầy đủ, đặc biệt là Nav2, SLAM, topic camera/depth thực tế, và logic nhặt/thả rác.

### Những phần đã làm được

| Hạng mục | Hiện trạng |
|---|---|
| Workspace ROS2 | Có `clean_robot_ws` với 6 package chính. |
| Webots world | Có `clean_robot_simulation/worlds/my_world.wbt`. |
| Robot trong Webots | Có robot tên `my_robot`, controller `<extern>`, hai bánh, camera, depth camera, LiDAR, GPS, IMU. |
| Driver Webots | Có `MyRobotDriver` trong `my_robot_driver.py`. |
| Điều khiển `/cmd_vel` | Driver subscribe `/cmd_vel` và chuyển thành vận tốc bánh trái/phải. |
| Manual command | Có node `simulation_test_node` nhận `/robot/manual_cmd` và publish `/cmd_vel`. |
| Odometry | Driver publish `/odom`. |
| TF động | Driver publish TF `odom -> base_footprint`. |
| TF robot model | `robot_state_publisher` dùng URDF/Xacro và `/joint_states` để tạo TF các link. |
| LiDAR | Webots/Xacro khai báo topic `/scan`. |
| Camera RGB | Webots/Xacro khai báo camera `rgb_camera`, topic gốc `/camera/image_raw`. |
| Depth camera | Webots/Xacro khai báo `depth_camera`, topic gốc `/depth_camera/image_depth`. |
| Message custom | Có `TrashDetection2D`, `TrashDetection2DArray`, `TrashCandidate`, `TrashCandidateArray`. |
| Perception | Có detector YOLO, localization bằng depth + TF, tracker theo số lần quan sát. |
| Mission | Có target manager và mission manager gửi goal Nav2. |
| SLAM | Có launch `slam.launch.py`, config `slam_params.yaml`, node chuẩn hóa scan. |
| Nav2 | Có `nav2.launch.py` và `nav2_params.yaml`. |
| RViz SLAM | Có `clean_robot_navigation/rviz/slam.rviz`. |
| Map | Có `maps/my_map.yaml` và `maps/my_map.pgm`. |

### Những phần chưa làm xong hoặc cần kiểm chứng

| Hạng mục | Trạng thái |
|---|---|
| Nhặt rác/thả rác vật lý | **Chưa hoàn thiện**. Mission mới publish event khi tới rác, chưa có cơ cấu nhặt/thả. |
| Nav2 với static map | **Cần bổ sung/kiểm chứng**. `nav2.launch.py` dùng `navigation_launch.py`, chưa thấy launch riêng cho `map_server` + `amcl` với `maps/my_map.yaml`. |
| AMCL | Có tham số trong `nav2_params.yaml`, nhưng launch hiện tại chưa khởi động localization riêng. |
| Webots ros2_control launch | `webots_control.launch.py` đang trỏ tới `clean_room.wbt`, nhưng source hiện chỉ có `my_world.wbt`; launch này có khả năng lỗi nếu chạy trực tiếp. |
| `robot_view.rviz` trong description | File đang rỗng 0 byte. |
| Topic camera/depth | URDF khai báo `/camera/image_raw` và `/depth_camera/image_depth`; perception mặc định dùng `/camera/image_raw/image_color` và `/depth_camera/image_depth/image`. Cần kiểm tra topic thực tế bằng `ros2 topic list`. |
| YOLO dependency | Code import `ultralytics`, nhưng dependency này chưa được khai báo trong `package.xml`. Cần cài thủ công khi chạy detector thật. |
| Service/action custom | Chưa thấy `.srv` hoặc `.action` custom trong `clean_robot_msgs`. Mission chỉ dùng action chuẩn `nav2_msgs/action/NavigateToPose`. |
| Package `clean_robot_base`, `clean_robot_bringup` | README cũ có nhắc, nhưng hiện không tồn tại trong `clean_robot_ws/src`. |

### Những phần dự kiến phát triển tiếp

- Làm chắc simulation: `/cmd_vel`, `/odom`, `/tf`, `/clock`, `/scan`, camera, depth.
- Đồng bộ tên topic camera/depth giữa Webots và perception.
- Chạy SLAM ổn định với `/scan_normalized`.
- Hoàn thiện Nav2 launch cho cả hai chế độ: dùng SLAM online và dùng static map.
- Hoàn thiện perception nhận diện rác thực tế trong Webots world.
- Chuyển detection 2D + depth thành target pose ổn định trong `map` hoặc `odom`.
- Hoàn thiện mission: tìm rác, đi tới rác, nhặt, đi tới điểm thả, thả rác.

---

## 2. Kiến trúc tổng thể

Luồng dữ liệu mong muốn của hệ thống:

```text
Webots Simulation
→ Sensor / Robot Driver
→ ROS2 Topics
→ Perception
→ Navigation / SLAM / Nav2
→ Mission Manager
→ Robot Command /cmd_vel
→ Webots Robot
```

Trong source hiện tại, các khối chính hoạt động như sau:

- `clean_robot_simulation` chạy Webots, kết nối robot `my_robot` với ROS2, nhận `/cmd_vel`, publish `/odom`, `/tf`, `/joint_states`, và để Webots ROS2 driver publish sensor.
- `clean_robot_description` mô tả robot bằng URDF/Xacro: base, bánh xe, LiDAR, camera.
- `clean_robot_navigation` chạy SLAM/Nav2 và chuẩn hóa dữ liệu LiDAR từ `/scan` sang `/scan_normalized`.
- `clean_robot_perception` nhận ảnh RGB/depth, tạo detection/candidate/tracked candidate cho rác.
- `clean_robot_mission` chọn target rác, gửi goal cho Nav2, publish trạng thái nhiệm vụ.
- `clean_robot_msgs` định nghĩa message custom dùng chung giữa perception và mission.

Sơ đồ Mermaid:

```mermaid
flowchart LR
    A[Webots Robot: my_robot] --> B[clean_robot_simulation]
    B --> C[/odom /tf /joint_states /clock]
    A --> S[/scan /camera /depth_camera]
    S --> D[clean_robot_perception]
    D --> T[/trash/detections /trash/candidates /trash/tracked_candidates]
    T --> E[clean_robot_mission]
    C --> F[clean_robot_navigation: SLAM / Nav2]
    S --> F
    E --> G[NavigateToPose action]
    G --> F
    F --> H[/cmd_vel]
    E --> H
    H --> B
    B --> A
```

---

## 3. Cấu trúc thư mục dự án

Các thư mục `build/`, `install/`, `log/` trong `clean_robot_ws` là output sinh ra bởi `colcon build` và các lần chạy trước. Người mới nên tập trung vào `clean_robot_ws/src`.

```text
CleanRobot_STU/
├── README.md
├── robot.urdf
├── docs/
│   ├── CleanRobot_STU_TEAM_GUIDE.pdf
│   ├── images/
│   │   └── kientructongquan.jpg
│   └── venv_for_in_wb/
│       └── tmpl0bd3p7h_world_with_URDF_robot.wbt
└── clean_robot_ws/
    ├── src/
    │   ├── clean_robot_description/
    │   │   ├── CMakeLists.txt
    │   │   ├── package.xml
    │   │   ├── config/
    │   │   │   └── controllers.yaml
    │   │   ├── launch/
    │   │   │   └── display.launch.py
    │   │   ├── rviz/
    │   │   │   └── robot_view.rviz
    │   │   └── urdf/
    │   │       ├── clean_robot.urdf.xacro
    │   │       ├── base.urdf.xacro
    │   │       ├── wheels.urdf.xacro
    │   │       └── sensors.urdf.xacro
    │   ├── clean_robot_simulation/
    │   │   ├── package.xml
    │   │   ├── setup.py
    │   │   ├── clean_robot_simulation/
    │   │   │   ├── my_robot_driver.py
    │   │   │   └── clean_robot_simulation.py
    │   │   ├── launch/
    │   │   │   ├── robot_launch.py
    │   │   │   └── webots_control.launch.py
    │   │   ├── worlds/
    │   │   │   └── my_world.wbt
    │   │   ├── resource/
    │   │   │   └── my_robot.urdf
    │   │   └── config/
    │   │       └── ros2_control.yaml
    │   ├── clean_robot_msgs/
    │   │   ├── CMakeLists.txt
    │   │   ├── package.xml
    │   │   └── msg/
    │   │       ├── TrashDetection2D.msg
    │   │       ├── TrashDetection2DArray.msg
    │   │       ├── TrashCandidate.msg
    │   │       └── TrashCandidateArray.msg
    │   ├── clean_robot_perception/
    │   │   ├── package.xml
    │   │   ├── setup.py
    │   │   ├── launch/
    │   │   │   └── perception.launch.py
    │   │   └── clean_robot_perception/
    │   │       ├── yolo_model.py
    │   │       ├── trash_detector_node.py
    │   │       ├── trash_localization_node.py
    │   │       ├── trash_tracker_node.py
    │   │       ├── fake_trash_candidate_node.py
    │   │       └── image_utils.py
    │   ├── clean_robot_navigation/
    │   │   ├── CMakeLists.txt
    │   │   ├── package.xml
    │   │   ├── config/
    │   │   │   ├── slam_params.yaml
    │   │   │   └── nav2_params.yaml
    │   │   ├── launch/
    │   │   │   ├── mapping.launch.py
    │   │   │   ├── slam.launch.py
    │   │   │   ├── nav2.launch.py
    │   │   │   └── rviz.launch.py
    │   │   ├── maps/
    │   │   │   ├── my_map.yaml
    │   │   │   └── my_map.pgm
    │   │   ├── rviz/
    │   │   │   └── slam.rviz
    │   │   └── scripts/
    │   │       └── scan_normalizer_node.py
    │   ├── clean_robot_mission/
    │   │   ├── package.xml
    │   │   ├── setup.py
    │   │   ├── launch/
    │   │   │   └── mission.launch.py
    │   │   └── clean_robot_mission/
    │   │       ├── mission_manager_node.py
    │   │       ├── target_manager_node.py
    │   │       ├── nav2_client.py
    │   │       ├── target_store.py
    │   │       ├── search_behavior.py
    │   │       └── state_machine.py
    │   └── slam_parmas.yaml
    ├── build/
    ├── install/
    └── log/
```

### Giải thích nhanh các thư mục/file quan trọng

| Đường dẫn | Vai trò |
|---|---|
| `README.md` | Hướng dẫn cũ/tổng quan ngắn của repo. Có một số package cũ được nhắc nhưng hiện không tồn tại trong `src`. |
| `robot.urdf` | File URDF sinh từ xacro trước đó, nằm ngoài package. Có vẻ là file tham khảo/phát sinh, không phải file chính đang được launch. |
| `docs/` | Tài liệu và hình ảnh tham khảo. |
| `clean_robot_ws/src` | Source chính của workspace ROS2. |
| `clean_robot_ws/src/slam_parmas.yaml` | File cấu hình SLAM rời, tên có lỗi chính tả `parmas`; launch hiện dùng `clean_robot_navigation/config/slam_params.yaml`, không dùng file này. |
| `build/`, `install/`, `log/` | Output của colcon. Có thể xóa và build lại khi cần, nhưng không sửa source trong đó. |

---

## 4. Giải thích từng package

### Package: `clean_robot_msgs`

#### Mục đích

Package này định nghĩa message custom dùng chung giữa perception và mission. Hiện có message cho detection 2D từ ảnh và candidate rác có pose trong không gian.

#### File quan trọng

| File | Vai trò |
|---|---|
| `msg/TrashDetection2D.msg` | Một bounding box rác trong ảnh 2D. |
| `msg/TrashDetection2DArray.msg` | Danh sách nhiều detection trong một frame ảnh. |
| `msg/TrashCandidate.msg` | Một ứng viên rác đã có `PoseStamped`, confidence, trạng thái và reachable. |
| `msg/TrashCandidateArray.msg` | Danh sách nhiều candidate rác. |
| `CMakeLists.txt` | Khai báo `rosidl_generate_interfaces`. |
| `package.xml` | Khai báo dependency `std_msgs`, `geometry_msgs`, `rosidl_default_generators`. |

#### Message hiện có

`TrashDetection2D.msg`:

```text
std_msgs/Header header
string class_name
float32 confidence
int32 x
int32 y
int32 width
int32 height
```

`TrashCandidate.msg`:

```text
std_msgs/Header header
string id
string class_name
float32 confidence
geometry_msgs/PoseStamped pose
bool reachable
string status
```

#### Node chính

Không có node chạy trong package này. Đây là package interface.

#### Topic subscribe/publish

Package này không trực tiếp subscribe/publish topic. Các message của nó đang được dùng bởi:

| Topic | Kiểu message | Node sử dụng |
|---|---|---|
| `/trash/detections` | `clean_robot_msgs/msg/TrashDetection2DArray` | `trash_detector_node`, `trash_localization_node` |
| `/trash/candidates` | `clean_robot_msgs/msg/TrashCandidateArray` | `trash_localization_node`, `trash_tracker_node`, `fake_trash_candidate_node` |
| `/trash/tracked_candidates` | `clean_robot_msgs/msg/TrashCandidateArray` | `trash_tracker_node`, `target_manager_node` |

#### Service/action

Chưa có `.srv` hoặc `.action` custom trong package này.

#### Cách build

```bash
cd ~/Truong_STU/CleanRobot_STU/clean_robot_ws
colcon build --packages-select clean_robot_msgs
source install/setup.bash
```

#### Cách kiểm tra

```bash
ros2 interface show clean_robot_msgs/msg/TrashDetection2D
ros2 interface show clean_robot_msgs/msg/TrashCandidate
```

#### Lỗi thường gặp

| Lỗi | Nguyên nhân có thể | Cách sửa |
|---|---|---|
| `Package 'clean_robot_msgs' not found` | Chưa build hoặc chưa source workspace. | Build lại và chạy `source install/setup.bash`. |
| Python node không import được `clean_robot_msgs.msg` | `clean_robot_msgs` chưa build trước package Python phụ thuộc. | Build toàn workspace hoặc build `clean_robot_msgs` trước. |

---

### Package: `clean_robot_description`

#### Mục đích

Package này mô tả hình học robot và cây frame bằng URDF/Xacro. Nó định nghĩa:

- `base_footprint`
- `base_link`
- `left_wheel_link`
- `right_wheel_link`
- `lidar_link`
- `camera_link`
- joint cố định và joint bánh xe
- phần Webots plugin/device mapping trong `clean_robot.urdf.xacro`

#### File quan trọng

| File | Vai trò |
|---|---|
| `urdf/clean_robot.urdf.xacro` | File xacro tổng, include base/wheels/sensors, khai báo Webots plugin và device ROS topics. |
| `urdf/base.urdf.xacro` | Khai báo `base_footprint`, `base_link`, joint cố định giữa hai frame. |
| `urdf/wheels.urdf.xacro` | Khai báo hai bánh và joint bánh xe. |
| `urdf/sensors.urdf.xacro` | Khai báo `lidar_link`, `camera_link` và vị trí sensor trên robot. |
| `config/controllers.yaml` | Cấu hình controller manager/diff drive theo tên joint URDF. |
| `launch/display.launch.py` | Launch `robot_state_publisher`, `rviz2`, và spawner controller. |
| `rviz/robot_view.rviz` | Hiện đang rỗng 0 byte. |

#### Webots mapping trong xacro

`clean_robot.urdf.xacro` khai báo:

| Webots device reference | Type | Topic ROS khai báo | Frame |
|---|---|---|---|
| `rgb_camera` | `Camera` | `/camera/image_raw` | `camera_link` |
| `depth_camera` | `RangeFinder` | `/depth_camera/image_depth` | Chưa khai báo `frameName` trong xacro hiện tại |
| `lidar` | `Lidar` | `/scan` | `lidar_link` |
| `gps` | `GPS` | Không đặt topic riêng trong xacro | Dùng nội bộ bởi driver nếu Webots device tồn tại |
| `inertial_unit` | `InertialUnit` | Không đặt topic riêng trong xacro | Dùng nội bộ bởi driver nếu Webots device tồn tại |

#### Node chính

Package không có executable riêng. Launch `display.launch.py` gọi node từ package khác:

| Node | Package | Vai trò |
|---|---|---|
| `robot_state_publisher` | `robot_state_publisher` | Publish TF cố định/dynamic từ URDF và `/joint_states`. |
| `rviz2` | `rviz2` | Mở giao diện quan sát. |
| `spawner joint_state_broadcaster` | `controller_manager` | Cần controller manager đang chạy. |
| `spawner diff_drive_controller` | `controller_manager` | Cần controller manager đang chạy. |

#### Topic subscribe/publish

| Topic | Kiểu message | Vai trò |
|---|---|---|
| `/robot_description` | `std_msgs/msg/String` hoặc parameter/topic robot description | Robot model cho RViz/robot_state_publisher. |
| `/joint_states` | `sensor_msgs/msg/JointState` | Input cho `robot_state_publisher` để publish TF bánh xe. |
| `/tf` | `tf2_msgs/msg/TFMessage` | TF động/cố định theo robot model. |
| `/tf_static` | `tf2_msgs/msg/TFMessage` | TF cố định. |

#### Service/action

Không có service/action custom.

#### Cách chạy

Chạy riêng phần hiển thị URDF:

```bash
cd ~/Truong_STU/CleanRobot_STU/clean_robot_ws
source install/setup.bash
ros2 launch clean_robot_description display.launch.py
```

Lưu ý: launch này có spawner controller. Nếu không có `controller_manager` đang chạy, spawner có thể báo lỗi. Khi chạy mô phỏng chính, `robot_launch.py` của simulation đã tự chạy `robot_state_publisher`.

#### Cách kiểm tra

```bash
ros2 topic list
ros2 topic echo /joint_states
ros2 run tf2_tools view_frames
```

Trong RViz, thêm:

- `TF`
- `RobotModel`

#### Lỗi thường gặp

| Lỗi | Nguyên nhân có thể | Cách sửa |
|---|---|---|
| RViz không hiện robot | Chưa có `/robot_description`, chưa chạy `robot_state_publisher`, hoặc chưa source workspace. | Chạy đúng launch và kiểm tra `ros2 topic list`. |
| TF thiếu `camera_link`/`lidar_link` | Chưa có `/joint_states` hoặc `robot_state_publisher` chưa chạy. | Kiểm tra `/joint_states`, `/tf`, launch simulation chính. |
| Spawner controller lỗi | Không có `controller_manager`. | Chỉ dùng `display.launch.py` để xem URDF, hoặc chạy mô phỏng/controller phù hợp trước. |

---

### Package: `clean_robot_simulation`

#### Mục đích

Package này chịu trách nhiệm chạy Webots và kết nối robot mô phỏng với ROS2. Đây là package quan trọng nhất ở giai đoạn hiện tại.

Nó có hai phần chính:

- `MyRobotDriver`: driver Webots nhận `/cmd_vel`, điều khiển motor, publish `/odom`, `/tf`, `/joint_states`.
- `ManualCmdNode`: node test nhận lệnh chữ qua `/robot/manual_cmd` và chuyển thành `/cmd_vel`.

#### File quan trọng

| File | Vai trò |
|---|---|
| `clean_robot_simulation/my_robot_driver.py` | Webots driver chính. |
| `clean_robot_simulation/clean_robot_simulation.py` | Node manual command, entry point là `simulation_test_node`. |
| `launch/robot_launch.py` | Launch chính để chạy Webots world, WebotsController, robot_state_publisher, manual command node. |
| `launch/webots_control.launch.py` | Launch thử nghiệm ros2_control. Hiện trỏ tới `clean_room.wbt`, trong source không có file này nên cần sửa trước khi dùng. |
| `worlds/my_world.wbt` | World Webots chính. |
| `config/ros2_control.yaml` | Cấu hình diff drive controller thử nghiệm. |
| `setup.py` | Đăng ký executable `simulation_test_node`. |
| `package.xml` | Khai báo dependency `webots_ros2_driver`, `geometry_msgs`, `sensor_msgs`, `nav_msgs`, `tf2_ros`, `rclpy`, `std_msgs`, `xacro`, `clean_robot_description`. |

#### Node chính

| Node/executable | Vai trò |
|---|---|
| `my_robot_driver_node` | Node được tạo trong `MyRobotDriver`, subscribe `/cmd_vel`, publish `/odom`, `/joint_states`, TF. |
| `simulation_test_node` | Node manual command, nhận `/robot/manual_cmd`, publish `/cmd_vel`. |
| `robot_state_publisher` | Được launch bởi `robot_launch.py`, publish TF robot model từ URDF. |
| Webots supervisor/controller | Do `webots_ros2_driver` tạo khi launch Webots. |

#### Topic sử dụng

| Topic | Kiểu message | Subscribe/Publish | Vai trò |
|---|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Driver subscribe, manual node publish | Lệnh vận tốc chuẩn để điều khiển robot. |
| `/robot/manual_cmd` | `std_msgs/msg/String` | Manual node subscribe | Lệnh chữ: `FORWARD`, `BACKWARD`, `LEFT`, `RIGHT`, `STOP`. |
| `/odom` | `nav_msgs/msg/Odometry` | Driver publish | Odometry `odom -> base_footprint`. |
| `/tf` | `tf2_msgs/msg/TFMessage` | Driver và robot_state_publisher publish | TF động và TF robot model. |
| `/joint_states` | `sensor_msgs/msg/JointState` | Driver publish | Vị trí joint bánh xe cho robot_state_publisher. |
| `/clock` | `rosgraph_msgs/msg/Clock` | Webots publish | Thời gian mô phỏng khi dùng `use_sim_time`. |
| `/scan` | `sensor_msgs/msg/LaserScan` | Webots ROS2 driver publish | Dữ liệu LiDAR. |
| `/camera/image_raw` hoặc topic con | `sensor_msgs/msg/Image` | Webots ROS2 driver publish | Ảnh RGB. |
| `/depth_camera/image_depth` hoặc topic con | `sensor_msgs/msg/Image` hoặc dữ liệu RangeFinder | Webots ROS2 driver publish | Ảnh chiều sâu. |

#### Webots world hiện tại

`worlds/my_world.wbt` có:

| Thành phần | Chi tiết |
|---|---|
| Robot name | `my_robot` |
| Controller | `<extern>` |
| Motor trái | `left wheel motor` |
| Motor phải | `right wheel motor` |
| Encoder trái | `left wheel sensor` |
| Encoder phải | `right wheel sensor` |
| Camera RGB | device name `rgb_camera`, 640x480, FOV 1.0472 |
| Depth camera | device name `depth_camera`, 320x240, range 0.05-3 m |
| LiDAR | 360 rays, FOV 2*pi, range 0.05-5 m |
| GPS | `gps` |
| IMU | `inertial_unit` |
| Distance sensors | `ds0`, `ds1`; hiện chưa thấy driver ROS2 riêng dùng hai sensor này. |
| Object rác/môi trường | Có `Can`, `WaterBottle`, `WoodenBox`, `Wall`, `CircleArena`. |

Lưu ý: trong `.wbt`, LiDAR không thấy dòng `name "lidar"` rõ ràng, trong khi xacro dùng `<device reference="lidar" type="Lidar">`. Nếu `/scan` không xuất hiện, cần kiểm tra lại tên device LiDAR trong Webots và `device reference` trong xacro.

#### Service/action

Không có service/action custom trong package này.

#### Cách chạy

Launch chính:

```bash
cd ~/Truong_STU/CleanRobot_STU/clean_robot_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch clean_robot_simulation robot_launch.py
```

Khi chạy thành công cần thấy:

- Webots mở world `my_world.wbt`.
- Robot `my_robot` xuất hiện trong arena.
- Webots không đứng mãi ở trạng thái chờ extern controller.
- Có node ROS2 của Webots/driver.
- Có topic `/cmd_vel`, `/odom`, `/tf`, `/joint_states`, `/clock`.
- Nếu sensor mapping đúng, có `/scan`, camera, depth camera.

#### Cách kiểm tra

```bash
ros2 node list
ros2 topic list
ros2 topic echo /clock
ros2 topic echo /odom
ros2 topic echo /tf
ros2 topic echo /joint_states
ros2 topic echo /scan
```

Điều khiển thử:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.15}, angular: {z: 0.0}}"
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

#### Lỗi thường gặp

| Lỗi | Nguyên nhân có thể | Cách kiểm tra | Cách sửa |
|---|---|---|---|
| Robot không di chuyển | Chưa publish `/cmd_vel`, driver không subscribe, motor name sai, robot name sai, Webots controller chưa kết nối. | `ros2 topic echo /cmd_vel`, `ros2 topic info /cmd_vel`, `ros2 node list`. | Chạy `robot_launch.py`, kiểm tra robot name `my_robot`, motor name trong `.wbt`, publish lệnh STOP/FORWARD. |
| `/odom` không đổi | Robot chưa di chuyển, driver không publish, GPS/IMU/encoder chưa enable, `/clock` không chạy. | `ros2 topic echo /odom`, `ros2 topic hz /odom`, `ros2 topic echo /clock`. | Kiểm tra driver log, Webots devices, `/cmd_vel`. |
| Webots báo waiting for extern controller | Robot `.wbt` dùng controller `<extern>` nhưng ROS2 WebotsController chưa kết nối. | Xem terminal launch. | Kiểm tra `robot_name='my_robot'`, xacro/plugin, Webots world, `webots_ros2_driver`. |
| Sensor không có topic | Webots device chưa map đúng, device reference không khớp, device chưa alwaysOn. | `ros2 topic list`, kiểm tra `.wbt` và xacro. | Đồng bộ tên device trong `.wbt` với `clean_robot.urdf.xacro`. |
| `webots_control.launch.py` lỗi world không tồn tại | File launch trỏ `clean_room.wbt`. | `ls worlds/`. | Sửa launch sang `my_world.wbt` hoặc không dùng launch này. |

---

### Package: `clean_robot_perception`

#### Mục đích

Package này xử lý camera/depth để phát hiện và định vị rác. Hiện đã có pipeline:

```text
RGB Image
→ trash_detector_node
→ /trash/detections
→ trash_localization_node + depth + TF
→ /trash/candidates
→ trash_tracker_node
→ /trash/tracked_candidates
```

#### File quan trọng

| File | Vai trò |
|---|---|
| `trash_detector_node.py` | Nhận ảnh RGB, chạy YOLO, publish detection 2D. |
| `yolo_model.py` | Wrapper cho `ultralytics.YOLO`. |
| `trash_localization_node.py` | Nhận detection + depth, tính điểm 3D, transform sang frame target. |
| `trash_tracker_node.py` | Đếm số lần quan sát candidate và chỉ publish khi đủ `min_observations`. |
| `fake_trash_candidate_node.py` | Node test publish candidate giả lên `/trash/candidates`. |
| `image_utils.py` | Hàm tiện ích tính tâm bbox. |
| `launch/perception.launch.py` | Launch detector, localization, tracker. |
| `setup.py` | Đăng ký executable perception. |

#### Node chính

| Executable | Node name | Vai trò |
|---|---|---|
| `trash_detector_node` | `trash_detector_node` | Detect rác từ ảnh RGB bằng YOLO. |
| `trash_localization_node` | `trash_localization_node` | Dùng depth + TF để tạo `TrashCandidate`. |
| `trash_tracker_node` | `trash_tracker_node` | Lọc candidate theo số lần quan sát. |
| `fake_trash_candidate_node` | `fake_trash_candidate_node` | Test mission mà không cần YOLO/depth. |

#### Topic sử dụng

| Topic | Kiểu message | Subscribe/Publish | Vai trò |
|---|---|---|---|
| `/camera/image_raw/image_color` | `sensor_msgs/msg/Image` | `trash_detector_node` subscribe mặc định | Ảnh RGB đầu vào cho YOLO. |
| `/trash/detections` | `clean_robot_msgs/msg/TrashDetection2DArray` | Detector publish, localization subscribe | Bounding boxes rác trong ảnh. |
| `/depth_camera/image_depth/image` | `sensor_msgs/msg/Image` | `trash_localization_node` subscribe mặc định | Ảnh depth để ước lượng khoảng cách. |
| `/tf` | `tf2_msgs/msg/TFMessage` | localization dùng TF buffer | Transform từ camera frame sang target frame. |
| `/trash/candidates` | `clean_robot_msgs/msg/TrashCandidateArray` | localization/fake publish, tracker subscribe | Candidate rác đã có pose. |
| `/trash/tracked_candidates` | `clean_robot_msgs/msg/TrashCandidateArray` | tracker publish | Candidate đã quan sát đủ lần. |

Lưu ý quan trọng: Webots/Xacro khai báo topic gốc là `/camera/image_raw` và `/depth_camera/image_depth`, nhưng code perception mặc định dùng `/camera/image_raw/image_color` và `/depth_camera/image_depth/image`. Webots ROS2 driver có thể tạo topic con tùy device. Luôn kiểm tra bằng:

```bash
ros2 topic list | sort
```

Nếu topic thực tế khác, chạy node bằng tham số phù hợp hoặc sửa launch.

#### Tham số quan trọng

`trash_detector_node`:

| Parameter | Mặc định | Ý nghĩa |
|---|---|---|
| `image_topic` | `/camera/image_raw/image_color` | Topic ảnh RGB. |
| `model_path` | `yolov8n.pt` | Đường dẫn model YOLO. |
| `confidence_threshold` | `0.35` | Ngưỡng confidence. |
| `target_classes` | `bottle,cup,bowl` | Lớp object được xem là rác. |

`trash_localization_node`:

| Parameter | Mặc định | Ý nghĩa |
|---|---|---|
| `depth_topic` | `/depth_camera/image_depth/image` | Topic ảnh depth. |
| `target_frame` | `map` | Frame đầu ra cho pose candidate. |
| `camera_frame` | `camera_link` | Frame camera. |
| `horizontal_fov` | `1.0472` | FOV ngang, khớp world Webots. |
| `depth_scale` | `1.0` | Hệ số đổi đơn vị depth sang mét. |
| `min_depth_m` | `0.05` | Khoảng cách nhỏ nhất hợp lệ. |
| `max_depth_m` | `3.0` | Khoảng cách lớn nhất hợp lệ. |
| `depth_sample_window` | `5` | Cửa sổ lấy median depth quanh tâm bbox. |
| `id_grid_m` | `0.25` | Kích thước lưới để tạo id candidate. |

`trash_tracker_node`:

| Parameter | Mặc định | Ý nghĩa |
|---|---|---|
| `min_observations` | `3` | Cần thấy cùng id đủ 3 lần mới publish tracked candidate. |

#### Service/action

Không có service/action custom.

#### Cách chạy

Chạy pipeline thật:

```bash
cd ~/Truong_STU/CleanRobot_STU/clean_robot_ws
source install/setup.bash
ros2 launch clean_robot_perception perception.launch.py
```

Chạy fake candidate để test mission không cần camera/depth:

```bash
ros2 run clean_robot_perception fake_trash_candidate_node
```

#### Cách kiểm tra

```bash
ros2 topic echo /trash/detections
ros2 topic echo /trash/candidates
ros2 topic echo /trash/tracked_candidates
ros2 topic hz /camera/image_raw/image_color
ros2 topic hz /depth_camera/image_depth/image
```

#### Lỗi thường gặp

| Lỗi | Nguyên nhân có thể | Cách sửa |
|---|---|---|
| `ModuleNotFoundError: ultralytics` | Chưa cài thư viện YOLO. | Cài `ultralytics` trong đúng môi trường Python đang chạy ROS2. |
| Không thấy detection | Sai topic ảnh, model không load, class filter không khớp, confidence quá cao. | Kiểm tra topic ảnh, thử giảm threshold, kiểm tra `model_path`. |
| Localization warn `No depth image received yet` | Chưa có depth topic hoặc topic sai. | Kiểm tra `ros2 topic list`, sửa `depth_topic`. |
| Warn transform `camera_link -> map` | Chưa có TF `map`, chưa chạy SLAM/Nav2, hoặc frame sai. | Chạy SLAM để có `map -> odom`, hoặc đổi `target_frame` sang `odom` khi test đơn giản. |
| Candidate không lên `/trash/tracked_candidates` | Tracker cần đủ `min_observations`. | Chờ thêm frame hoặc giảm `min_observations`. |

---

### Package: `clean_robot_navigation`

#### Mục đích

Package này chứa cấu hình SLAM, Nav2, RViz và map. Hiện package đã có:

- `scan_normalizer_node.py`: chuẩn hóa chiều dữ liệu LaserScan.
- `slam.launch.py`: chạy `slam_toolbox`.
- `mapping.launch.py`: chạy simulation + SLAM.
- `nav2.launch.py`: chạy Nav2 navigation stack với `nav2_params.yaml`.
- `rviz.launch.py`: mở RViz với config SLAM.
- `maps/my_map.yaml` và `maps/my_map.pgm`: map đã lưu.

#### File quan trọng

| File | Vai trò |
|---|---|
| `scripts/scan_normalizer_node.py` | Subscribe `/scan`, publish `/scan_normalized`. Nếu angle increment âm thì đảo ranges. |
| `config/slam_params.yaml` | Tham số `slam_toolbox`, dùng `/scan_normalized`, frame `odom`, `map`, `base_footprint`. |
| `config/nav2_params.yaml` | Tham số AMCL, planner, controller, BT navigator, behavior, costmap, velocity smoother, collision monitor. |
| `launch/slam.launch.py` | Chạy scan normalizer và `async_slam_toolbox_node` dạng lifecycle. |
| `launch/mapping.launch.py` | Include `clean_robot_simulation/robot_launch.py` và `slam.launch.py`. |
| `launch/nav2.launch.py` | Include `nav2_bringup/launch/navigation_launch.py` với `nav2_params.yaml`. |
| `launch/rviz.launch.py` | Mở RViz với `rviz/slam.rviz`. |
| `maps/my_map.yaml` | Metadata map, resolution 0.05, origin `[-3.206, -2.537, 0]`. |
| `maps/my_map.pgm` | Ảnh map kích thước 115x101. |
| `rviz/slam.rviz` | RViz config có Grid, Map `/map`, LaserScan `/scan_normalized`, RobotModel, TF, Fixed Frame `map`. |

#### Node chính

| Node | Package | Vai trò |
|---|---|---|
| `scan_normalizer_node` | `clean_robot_navigation` | Chuẩn hóa LaserScan. |
| `slam_toolbox` | `slam_toolbox` | Tạo map online từ LiDAR + TF + odom. |
| Nav2 nodes | `nav2_bringup`/Nav2 packages | Planner, controller, BT navigator, behavior server, costmap, velocity smoother... |
| `rviz2` | `rviz2` | Hiển thị map, TF, scan, robot. |

#### Topic sử dụng

| Topic | Kiểu message | Subscribe/Publish | Vai trò |
|---|---|---|---|
| `/scan` | `sensor_msgs/msg/LaserScan` | normalizer subscribe, Nav2 costmap dùng | LiDAR gốc từ Webots. |
| `/scan_normalized` | `sensor_msgs/msg/LaserScan` | normalizer publish, SLAM subscribe | Scan đã chuẩn hóa cho `slam_toolbox`. |
| `/odom` | `nav_msgs/msg/Odometry` | SLAM/Nav2 subscribe | Odometry robot. |
| `/tf` | `tf2_msgs/msg/TFMessage` | SLAM/Nav2 subscribe/publish | Cây frame. |
| `/map` | `nav_msgs/msg/OccupancyGrid` | SLAM publish hoặc map server publish | Bản đồ. |
| `/map_updates` | `map_msgs/msg/OccupancyGridUpdate` | SLAM publish | Cập nhật map. |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Nav2/collision monitor publish | Lệnh vận tốc ra robot. |
| `/goal_pose` | `geometry_msgs/msg/PoseStamped` | RViz/Nav2 dùng | Goal từ RViz. |
| `navigate_to_pose` | `nav2_msgs/action/NavigateToPose` | Nav2 action server | Mission gửi goal. |

#### Service/action

Package này không tự định nghĩa service/action custom, nhưng Nav2 cung cấp nhiều service/action. Mission đang dùng action:

```text
nav2_msgs/action/NavigateToPose
Action name: navigate_to_pose
```

#### Cách chạy SLAM

Chạy simulation + SLAM cùng lúc:

```bash
cd ~/Truong_STU/CleanRobot_STU/clean_robot_ws
source install/setup.bash
ros2 launch clean_robot_navigation mapping.launch.py
```

Hoặc nếu simulation đã chạy sẵn, chỉ chạy SLAM:

```bash
ros2 launch clean_robot_navigation slam.launch.py
```

Mở RViz:

```bash
ros2 launch clean_robot_navigation rviz.launch.py
```

#### Cách chạy Nav2

Khi simulation và SLAM/map đã chạy:

```bash
ros2 launch clean_robot_navigation nav2.launch.py
```

Lưu ý hiện trạng: `nav2.launch.py` include `navigation_launch.py`, chưa thấy include `map_server` hoặc `localization_launch.py` với `maps/my_map.yaml`. Vì vậy Nav2 nên được chạy cùng SLAM online để có `/map`, hoặc cần bổ sung launch static map + AMCL nếu muốn dùng `my_map.yaml`.

#### Cách kiểm tra

```bash
ros2 topic echo /scan
ros2 topic echo /scan_normalized
ros2 topic echo /map
ros2 lifecycle get /slam_toolbox
ros2 action list
ros2 action info /navigate_to_pose
```

#### Lỗi thường gặp

| Lỗi | Nguyên nhân có thể | Cách sửa |
|---|---|---|
| Không có `/scan_normalized` | `scan_normalizer_node.py` chưa chạy hoặc `/scan` không có. | Chạy `slam.launch.py`, kiểm tra `/scan`. |
| SLAM không tạo map | Thiếu `/scan`, `/odom`, `/tf`, `/clock`, robot đứng yên, frame sai. | Kiểm tra từng topic/frame và điều khiển robot di chuyển. |
| Nav2 action server không ready | Nav2 chưa launch đủ node hoặc lifecycle chưa active. | Kiểm tra `ros2 node list`, log Nav2, `ros2 action list`. |
| Nav2 không có map | Chưa chạy SLAM/map server. | Chạy SLAM hoặc bổ sung launch map server + AMCL. |
| Costmap không thấy obstacle | Sai `/scan`, thiếu TF `base_footprint -> lidar_link`. | Kiểm tra RViz TF và LaserScan. |

---

### Package: `clean_robot_mission`

#### Mục đích

Package này điều phối nhiệm vụ cấp cao. Hiện code đã có:

- `target_manager_node`: chọn candidate rác tốt nhất từ `/trash/tracked_candidates`.
- `mission_manager_node`: ở trạng thái tìm kiếm, nhận target pose, gửi goal tới Nav2 action `navigate_to_pose`, publish trạng thái/event.

Logic hiện tại là nền tảng mission, chưa có thao tác nhặt/thả rác thật.

#### File quan trọng

| File | Vai trò |
|---|---|
| `mission_manager_node.py` | State machine nhiệm vụ, gửi goal Nav2, publish `/cmd_vel` khi search/stop. |
| `target_manager_node.py` | Chọn candidate reachable có confidence cao nhất và publish target pose/id. |
| `nav2_client.py` | Wrapper cho action client `NavigateToPose`. |
| `state_machine.py` | Enum trạng thái mission. |
| `target_store.py` | Lưu target hiện tại. |
| `search_behavior.py` | Có danh sách waypoint mẫu nhưng hiện chưa được dùng trong `mission_manager_node.py`. |
| `launch/mission.launch.py` | Launch target manager và mission manager. |
| `setup.py` | Đăng ký executable `target_manager_node`, `mission_manager_node`. |

#### Node chính

| Executable | Node name | Vai trò |
|---|---|---|
| `target_manager_node` | `target_manager_node` | Chọn target từ tracked candidates. |
| `mission_manager_node` | `mission_manager_node` | Điều phối trạng thái và gửi Nav2 goal. |

#### Topic sử dụng

| Topic | Kiểu message | Subscribe/Publish | Vai trò |
|---|---|---|---|
| `/trash/tracked_candidates` | `clean_robot_msgs/msg/TrashCandidateArray` | target manager subscribe | Candidate rác đã ổn định. |
| `/trash/rejected_id` | `std_msgs/msg/String` | mission publish, target manager subscribe | Bỏ qua target thất bại. |
| `/trash/target_pose` | `geometry_msgs/msg/PoseStamped` | target manager publish, mission subscribe | Pose target gửi tới Nav2. |
| `/trash/target_id` | `std_msgs/msg/String` | target manager publish, mission subscribe | ID target hiện tại. |
| `/mission/state` | `std_msgs/msg/String` | mission publish | Trạng thái mission. |
| `/mission/event` | `std_msgs/msg/String` | mission publish | Event như `REACHED_TRASH`, `FAILED_TARGET`. |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | mission publish | Xoay tìm rác hoặc dừng robot. |

#### Action sử dụng

| Action | Kiểu | Vai trò |
|---|---|---|
| `navigate_to_pose` | `nav2_msgs/action/NavigateToPose` | Mission gửi goal target cho Nav2. |

#### State machine hiện tại

| State | Ý nghĩa trong code hiện tại |
|---|---|
| `SEARCHING` | Nếu chưa có target, publish twist tìm kiếm: `linear.x=0.0`, `angular.z=0.35`. Nếu có target, gửi Nav2 goal. |
| `NAVIGATING_TO_TRASH` | Chờ trạng thái action Nav2. |
| `REACHED_TRASH` | Publish stop, publish event `REACHED_TRASH`, clear target, quay lại `SEARCHING`. |
| `FAILED` | Publish stop, publish rejected target/event, clear target, quay lại `SEARCHING`. |
| `IDLE`, `NAVIGATING_SEARCH` | Có trong enum nhưng chưa thấy dùng trong `mission_manager_node.py`. |

#### Cách chạy

Mission cần perception và Nav2 nếu muốn chạy thật:

```bash
cd ~/Truong_STU/CleanRobot_STU/clean_robot_ws
source install/setup.bash
ros2 launch clean_robot_mission mission.launch.py
```

Test mission bằng fake candidate:

```bash
ros2 run clean_robot_perception fake_trash_candidate_node
ros2 launch clean_robot_mission mission.launch.py
```

Nếu muốn Nav2 nhận goal thành công, cần chạy simulation + SLAM/map + Nav2 trước.

#### Cách kiểm tra

```bash
ros2 topic echo /mission/state
ros2 topic echo /mission/event
ros2 topic echo /trash/target_pose
ros2 topic echo /trash/target_id
ros2 action info /navigate_to_pose
```

#### Lỗi thường gặp

| Lỗi | Nguyên nhân có thể | Cách sửa |
|---|---|---|
| Mission chỉ xoay robot mãi | Chưa có `/trash/tracked_candidates`. | Chạy perception hoặc fake candidate. |
| Log `Nav2 action server navigate_to_pose is not ready` | Nav2 chưa chạy hoặc chưa active. | Chạy `nav2.launch.py`, kiểm tra `ros2 action list`. |
| Goal bị reject/fail | Pose frame sai, không có map, costmap lỗi, target ngoài map. | Kiểm tra `target_pose.header.frame_id`, `/map`, `/tf`, Nav2 log. |
| Robot dừng ngay khi thấy target | Mission publish stop trước khi gửi goal, đây là behavior hiện tại. | Không phải lỗi nếu sau đó Nav2 tiếp quản `/cmd_vel`. |

---

## 5. Các topic ROS2 quan trọng

### `/cmd_vel`

Topic điều khiển vận tốc robot.

Message:

```text
geometry_msgs/msg/Twist
```

Ý nghĩa cơ bản:

| Trường | Ý nghĩa |
|---|---|
| `linear.x > 0` | Robot đi tới. |
| `linear.x < 0` | Robot đi lùi. |
| `angular.z > 0` | Robot xoay trái. |
| `angular.z < 0` | Robot xoay phải. |

Ví dụ:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.15}, angular: {z: 0.0}}"
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

Trong driver hiện tại, lệnh cuối được lưu trong `self.__target_twist`, nên nếu publish lệnh tiến một lần thì robot có thể tiếp tục chạy cho đến khi publish STOP hoặc node khác ghi đè `/cmd_vel`.

### `/robot/manual_cmd`

Topic lệnh chữ để test đơn giản.

Message:

```text
std_msgs/msg/String
```

Các lệnh node hiện hỗ trợ:

- `FORWARD`
- `BACKWARD`
- `LEFT`
- `RIGHT`
- `STOP`

Ví dụ:

```bash
ros2 topic pub --once /robot/manual_cmd std_msgs/msg/String "{data: 'FORWARD'}"
ros2 topic pub --once /robot/manual_cmd std_msgs/msg/String "{data: 'STOP'}"
```

### `/odom`

Topic odometry, cho biết robot di chuyển tương đối trong frame `odom`.

Message:

```text
nav_msgs/msg/Odometry
```

Driver hiện publish:

- `header.frame_id = odom`
- `child_frame_id = base_footprint`
- pose `x`, `y`, yaw
- twist `linear.x`, `angular.z`

Kiểm tra:

```bash
ros2 topic echo /odom
ros2 topic hz /odom
```

Nếu robot không di chuyển hoặc driver chưa publish, `/odom` có thể không đổi.

### `/tf`

Topic mô tả quan hệ giữa các frame.

Message:

```text
tf2_msgs/msg/TFMessage
```

Frame hiện có hoặc dự kiến trong dự án:

- `map`
- `odom`
- `base_footprint`
- `base_link`
- `left_wheel_link`
- `right_wheel_link`
- `lidar_link`
- `camera_link`

Kiểm tra:

```bash
ros2 run tf2_tools view_frames
```

Hoặc:

```bash
ros2 topic echo /tf
```

### `/joint_states`

Message:

```text
sensor_msgs/msg/JointState
```

Driver publish joint:

- `left_wheel_joint`
- `right_wheel_joint`

`robot_state_publisher` dùng topic này để cập nhật TF cho các link liên quan.

Kiểm tra:

```bash
ros2 topic echo /joint_states
```

### `/scan`

Topic LiDAR gốc từ Webots.

Message:

```text
sensor_msgs/msg/LaserScan
```

Dùng cho:

- SLAM
- Nav2 costmap
- RViz LaserScan

Kiểm tra:

```bash
ros2 topic echo /scan
ros2 topic hz /scan
```

### `/scan_normalized`

Topic do `scan_normalizer_node.py` publish. SLAM launch hiện dùng topic này thay vì `/scan`.

Kiểm tra:

```bash
ros2 topic echo /scan_normalized
ros2 topic hz /scan_normalized
```

### `/clock`

Topic thời gian mô phỏng. Khi chạy Webots và các node dùng `use_sim_time:=true`, `/clock` phải chạy.

Message:

```text
rosgraph_msgs/msg/Clock
```

Kiểm tra:

```bash
ros2 topic echo /clock
```

Nếu `/clock` không chạy, SLAM/Nav2/RViz có thể không cập nhật đúng.

### Camera RGB

URDF/Xacro khai báo topic gốc:

```text
/camera/image_raw
```

Perception code mặc định subscribe:

```text
/camera/image_raw/image_color
```

Kiểm tra topic thực tế:

```bash
ros2 topic list | sort
ros2 topic hz /camera/image_raw/image_color
```

Nếu topic khác, sửa parameter `image_topic`.

### Depth camera / RangeFinder

URDF/Xacro khai báo topic gốc:

```text
/depth_camera/image_depth
```

Perception code mặc định subscribe:

```text
/depth_camera/image_depth/image
```

Kiểm tra:

```bash
ros2 topic list | sort
ros2 topic hz /depth_camera/image_depth/image
```

### Topic perception/mission

| Topic | Message | Vai trò |
|---|---|---|
| `/trash/detections` | `clean_robot_msgs/msg/TrashDetection2DArray` | Detection 2D từ YOLO. |
| `/trash/candidates` | `clean_robot_msgs/msg/TrashCandidateArray` | Candidate có pose từ depth/TF. |
| `/trash/tracked_candidates` | `clean_robot_msgs/msg/TrashCandidateArray` | Candidate đã ổn định qua nhiều quan sát. |
| `/trash/target_pose` | `geometry_msgs/msg/PoseStamped` | Target pose mission gửi tới Nav2. |
| `/trash/target_id` | `std_msgs/msg/String` | ID target đang được chọn. |
| `/trash/rejected_id` | `std_msgs/msg/String` | Target đã fail, target manager bỏ qua. |
| `/mission/state` | `std_msgs/msg/String` | State mission hiện tại. |
| `/mission/event` | `std_msgs/msg/String` | Event mission. |

---

## 6. Hướng dẫn cài đặt môi trường

Source hiện tại và README đang hướng tới:

- Ubuntu 24.04 LTS
- ROS2 Jazzy Jalisco
- Webots
- `webots_ros2_driver`
- Nav2
- `slam_toolbox`

Kiểm tra distro ROS đang source:

```bash
echo $ROS_DISTRO
```

Trên máy được khảo sát, biến môi trường đang là:

```text
jazzy
```

### Cài ROS2 Jazzy

Nếu máy chưa có ROS2, cài theo hướng dẫn chính thức của ROS2 Jazzy. Các lệnh cơ bản thường dùng:

```bash
locale
sudo apt update
sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
```

```bash
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update
sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
```

```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

```bash
sudo apt update
sudo apt upgrade
sudo apt install ros-jazzy-desktop python3-argcomplete
```

Source ROS2:

```bash
source /opt/ros/jazzy/setup.bash
```

Có thể thêm vào `~/.bashrc`:

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
```

### Cài công cụ build

```bash
sudo apt install python3-colcon-common-extensions python3-rosdep python3-vcstool
```

Khởi tạo `rosdep` nếu máy chưa làm:

```bash
sudo rosdep init
rosdep update
```

Nếu `sudo rosdep init` báo đã tồn tại, bỏ qua và chạy `rosdep update`.

### Cài Webots

Theo README hiện tại:

```bash
sudo snap install webots
```

`robot_launch.py` có logic tự đặt `WEBOTS_HOME` nếu tìm thấy:

- `/snap/webots/current/usr/share/webots`
- `/usr/local/webots`

Nếu Webots nằm ở đường dẫn khác, cần export thủ công:

```bash
export WEBOTS_HOME=/duong/dan/toi/webots
```

### Cài cầu nối Webots ROS2

```bash
sudo apt install ros-jazzy-webots-ros2 ros-jazzy-webots-ros2-driver
```

### Cài Nav2, SLAM, RViz, TF tools

```bash
sudo apt install \
  ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup \
  ros-jazzy-slam-toolbox \
  ros-jazzy-tf2-tools \
  ros-jazzy-xacro \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-rviz2
```

### Cài dependency perception

Package perception cần:

- `cv_bridge`
- OpenCV
- NumPy
- `ultralytics` nếu chạy YOLO thật

```bash
sudo apt install ros-jazzy-cv-bridge python3-opencv python3-numpy
```

`ultralytics` hiện chưa được khai báo trong `package.xml`, nhưng `yolo_model.py` import trực tiếp:

```bash
python3 -m pip install --user ultralytics
```

Nếu Ubuntu chặn pip do môi trường Python được quản lý bởi hệ thống, cần dùng môi trường Python phù hợp với ROS2 của nhóm. Khi chạy node, phải đảm bảo Python đang thấy được cả ROS2 packages và `ultralytics`.

### Cài dependency bằng rosdep

```bash
cd ~/Truong_STU/CleanRobot_STU/clean_robot_ws
rosdep install --from-paths src --ignore-src -r -y
```

Lưu ý: `rosdep` chỉ cài dependency đã khai báo trong `package.xml`. Vì `ultralytics` chưa khai báo, có thể vẫn cần cài riêng.

---

## 7. Hướng dẫn build dự án

Build toàn bộ workspace:

```bash
cd ~/Truong_STU/CleanRobot_STU/clean_robot_ws
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash
```

Build một package:

```bash
colcon build --packages-select clean_robot_simulation
source install/setup.bash
```

Build nhiều package liên quan:

```bash
colcon build --packages-select clean_robot_msgs clean_robot_perception clean_robot_mission
source install/setup.bash
```

Kiểm tra package đã được ROS2 nhận:

```bash
ros2 pkg list | grep clean_robot
```

Các package hiện có trong workspace:

```text
clean_robot_description
clean_robot_mission
clean_robot_msgs
clean_robot_navigation
clean_robot_perception
clean_robot_simulation
```

### Khi nào cần build lại?

- Sửa `package.xml`, `setup.py`, `CMakeLists.txt`: cần build lại.
- Thêm executable Python mới: cần build lại.
- Sửa launch, URDF, yaml: nên build lại để file được copy sang `install/`.
- Sửa logic Python trong package `ament_python`: trong nhiều trường hợp vẫn nên build lại để tránh chạy nhầm bản cũ.
- Sau mọi lần build: luôn chạy `source install/setup.bash`.

### Lỗi build thường gặp

| Lỗi | Nguyên nhân | Cách xử lý |
|---|---|---|
| Không tìm thấy package ROS2 | Chưa source `/opt/ros/jazzy/setup.bash`. | Source ROS2 trước khi build. |
| Không tìm thấy `clean_robot_msgs` khi build perception/mission | Interface package chưa build hoặc dependency chưa đúng thứ tự. | Build toàn workspace hoặc build `clean_robot_msgs` trước. |
| Launch không thấy file mới sửa | Chưa build lại sau khi sửa file trong `src`. | `colcon build` rồi source lại. |

---

## 8. Hướng dẫn chạy mô phỏng Webots

Launch chính hiện tại:

```bash
cd ~/Truong_STU/CleanRobot_STU/clean_robot_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch clean_robot_simulation robot_launch.py
```

Launch này làm các việc:

- Mở Webots với world `clean_robot_simulation/worlds/my_world.wbt`.
- Bật `ros2_supervisor=True`.
- Kết nối `WebotsController` với robot name `my_robot`.
- Load `clean_robot_description/urdf/clean_robot.urdf.xacro`.
- Chạy `robot_state_publisher`.
- Chạy `simulation_test_node` để nhận `/robot/manual_cmd`.

Khi chạy thành công cần thấy:

- Webots mở lên.
- Robot xuất hiện trong world.
- Không có lỗi robot name/controller.
- ROS2 node chạy không báo lỗi nghiêm trọng.
- Có thể xem danh sách topic:

```bash
ros2 topic list
```

Các lệnh kiểm tra cơ bản:

```bash
ros2 node list
ros2 topic echo /clock
ros2 topic echo /odom
ros2 topic echo /scan
ros2 topic echo /joint_states
```

Nếu `/scan` chưa có, kiểm tra:

- Webots device LiDAR trong `.wbt`.
- `<device reference="lidar" type="Lidar">` trong xacro.
- Log của `webots_ros2_driver`.

Không nên dùng ngay:

```bash
ros2 launch clean_robot_simulation webots_control.launch.py
```

Vì launch này đang trỏ tới `clean_room.wbt`, nhưng source hiện tại chỉ có `my_world.wbt`. Đây là phần **cần sửa/bổ sung** nếu nhóm muốn dùng ros2_control thay vì driver Python custom.

---

## 9. Hướng dẫn điều khiển robot

Có hai cách điều khiển trong source hiện tại:

- Gửi trực tiếp `/cmd_vel`.
- Gửi lệnh chữ `/robot/manual_cmd`, node manual sẽ chuyển thành `/cmd_vel`.

### Điều khiển bằng `/robot/manual_cmd`

Topic:

```text
/robot/manual_cmd
```

Message:

```text
std_msgs/msg/String
```

Ví dụ:

```bash
ros2 topic pub --once /robot/manual_cmd std_msgs/msg/String "{data: 'FORWARD'}"
ros2 topic pub --once /robot/manual_cmd std_msgs/msg/String "{data: 'BACKWARD'}"
ros2 topic pub --once /robot/manual_cmd std_msgs/msg/String "{data: 'LEFT'}"
ros2 topic pub --once /robot/manual_cmd std_msgs/msg/String "{data: 'RIGHT'}"
ros2 topic pub --once /robot/manual_cmd std_msgs/msg/String "{data: 'STOP'}"
```

Thông số mặc định trong node:

| Parameter | Mặc định | Ý nghĩa |
|---|---|---|
| `linear_speed` | `0.15` | Tốc độ tiến/lùi. |
| `angular_speed` | `0.8` | Tốc độ xoay. |

### Điều khiển trực tiếp bằng `/cmd_vel`

Đi tới:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2}, angular: {z: 0.0}}"
```

Xoay trái:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.5}}"
```

Xoay phải:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: -0.5}}"
```

Dừng:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

Giải thích:

- `/robot/manual_cmd` là lệnh dạng chữ, dễ test khi mới học ROS2.
- `/cmd_vel` là lệnh vận tốc chuẩn của ROS2/Nav2.
- Robot Webots chỉ di chuyển nếu driver thật sự nhận `/cmd_vel` và chuyển thành tốc độ bánh xe.
- Trong driver hiện tại, lệnh `/cmd_vel` được lưu lại. Luôn publish STOP sau khi test.

---

## 10. Giải thích Webots driver

Driver chính nằm ở:

```text
clean_robot_ws/src/clean_robot_simulation/clean_robot_simulation/my_robot_driver.py
```

Class:

```python
class MyRobotDriver:
```

Driver được nạp từ xacro:

```xml
<plugin type="clean_robot_simulation.my_robot_driver.MyRobotDriver" />
```

### Driver lấy thiết bị bánh xe như thế nào?

Trong `init()`, driver lấy motor bằng tên Webots:

```python
self.__left_motor = self.__robot.getDevice('left wheel motor')
self.__right_motor = self.__robot.getDevice('right wheel motor')
```

Sau đó đặt motor sang chế độ velocity control:

```python
self.__left_motor.setPosition(float('inf'))
self.__left_motor.setVelocity(0.0)
self.__right_motor.setPosition(float('inf'))
self.__right_motor.setVelocity(0.0)
```

Điều này yêu cầu `.wbt` phải có đúng tên device:

```text
left wheel motor
right wheel motor
```

Trong `my_world.wbt`, hai tên này đang tồn tại.

### Driver lấy encoder như thế nào?

Driver lấy position sensor:

```python
self.__left_pos_sensor = self.__robot.getDevice('left wheel sensor')
self.__right_pos_sensor = self.__robot.getDevice('right wheel sensor')
```

Nếu có sensor, driver enable sensor theo basic timestep của Webots. Trong `my_world.wbt`, hai sensor này đang tồn tại.

### Driver lấy GPS/IMU như thế nào?

Driver lấy:

```python
self.__gps = self.__robot.getDevice('gps')
self.__imu = self.__robot.getDevice('inertial_unit')
```

Nếu có cả GPS và IMU, driver dùng ground-truth pose từ Webots để publish odometry ổn định hơn trong mô phỏng. Nếu không có, driver fallback sang encoder. Nếu cũng không có encoder, driver ước lượng odom từ command velocity.

### Driver nhận `/cmd_vel` như thế nào?

Driver tạo subscriber:

```python
self.__node.create_subscription(Twist, '/cmd_vel', self.__cmd_vel_callback, 1)
```

Callback lưu lệnh mới nhất:

```python
def __cmd_vel_callback(self, twist):
    self.__target_twist = twist
```

Trong mỗi bước Webots `step()`, driver lấy:

```python
forward_speed = self.__target_twist.linear.x
angular_speed = self.__target_twist.angular.z
```

### Công thức differential drive

Thông số trong driver:

```python
HALF_DISTANCE_BETWEEN_WHEELS = 0.045
WHEEL_RADIUS = 0.025
```

Tức:

- khoảng cách hai bánh `wheel_base = 0.09 m`
- bán kính bánh `wheel_radius = 0.025 m`

Công thức trong code:

```python
cmd_left  = (forward_speed - angular_speed * HALF_DISTANCE_BETWEEN_WHEELS) / WHEEL_RADIUS
cmd_right = (forward_speed + angular_speed * HALF_DISTANCE_BETWEEN_WHEELS) / WHEEL_RADIUS
```

Dạng tổng quát:

```text
left_speed  = (linear_velocity - angular_velocity * wheel_base / 2) / wheel_radius
right_speed = (linear_velocity + angular_velocity * wheel_base / 2) / wheel_radius
```

Ý nghĩa:

| Biến | Ý nghĩa |
|---|---|
| `linear_velocity` / `forward_speed` | Tốc độ tiến/lùi của robot. |
| `angular_velocity` / `angular_speed` | Tốc độ xoay quanh trục z. |
| `wheel_base` | Khoảng cách giữa hai bánh. |
| `wheel_radius` | Bán kính bánh xe. |
| `left_speed`, `right_speed` | Vận tốc góc đặt cho motor Webots. |

Sau khi tính, driver gọi:

```python
self.__left_motor.setVelocity(cmd_left)
self.__right_motor.setVelocity(cmd_right)
```

### Driver publish `/odom`

Driver publish:

```python
self.__odom_pub = self.__node.create_publisher(Odometry, '/odom', 10)
```

Odometry hiện dùng:

```text
header.frame_id = odom
child_frame_id = base_footprint
```

Nếu có GPS/IMU, driver lấy pose tương đối từ vị trí ban đầu trong Webots:

- `gps_values[0]`, `gps_values[1]`
- yaw từ `inertial_unit`
- chuẩn hóa yaw bằng `normalize_angle()`

Nếu không có GPS/IMU, driver dùng encoder:

- đọc `left wheel sensor`, `right wheel sensor`
- tính quãng đường bánh trái/phải
- cập nhật `x`, `y`, `theta`

### Driver publish `/tf`

Driver tạo `TransformBroadcaster` và publish TF:

```text
odom -> base_footprint
```

TF này là nền tảng cho SLAM/Nav2.

Các TF còn lại như:

```text
base_footprint -> base_link
base_link -> lidar_link
base_link -> camera_link
base_link -> wheel links
```

được tạo bởi `robot_state_publisher` từ URDF/Xacro và `/joint_states`.

### Driver publish `/joint_states`

Driver publish:

```python
self.__joint_state_pub = self.__node.create_publisher(JointState, '/joint_states', 10)
```

Tên joint:

```text
left_wheel_joint
right_wheel_joint
```

Nếu có encoder, vị trí joint lấy từ encoder. Nếu không có encoder, driver tích lũy từ command motor.

### Driver lấy LiDAR/camera/depth như thế nào?

`MyRobotDriver` không tự đọc LiDAR/camera/depth trong code Python. Các sensor này được khai báo trong xacro dưới thẻ `<webots><device ...>`, để `webots_ros2_driver` publish ra ROS2 topic.

Các mapping hiện tại:

```xml
<device reference="rgb_camera" type="Camera">
  <topicName>/camera/image_raw</topicName>
</device>

<device reference="depth_camera" type="RangeFinder">
  <topicName>/depth_camera/image_depth</topicName>
</device>

<device reference="lidar" type="Lidar">
  <topicName>/scan</topicName>
</device>
```

Nếu không thấy sensor topic:

- kiểm tra tên device trong `.wbt`
- kiểm tra `device reference` trong xacro
- kiểm tra Webots controller đã kết nối chưa
- kiểm tra `ros2 topic list`

### Những điểm cần chú ý về tên robot/controller

Trong `robot_launch.py`:

```python
my_robot_driver = WebotsController(
    robot_name='my_robot',
    ...
)
```

Trong `my_world.wbt`:

```text
Robot {
  name "my_robot"
  controller "<extern>"
}
```

Hai tên này phải khớp. Nếu không khớp, Webots có thể báo đang chờ extern controller hoặc ROS2 driver không điều khiển được robot.

---

## 11. Hướng dẫn kiểm tra sensor

### Kiểm tra LiDAR

```bash
ros2 topic echo /scan
ros2 topic hz /scan
```

Nếu dùng SLAM launch:

```bash
ros2 topic echo /scan_normalized
ros2 topic hz /scan_normalized
```

Trong RViz:

- Add `LaserScan`
- Topic: `/scan` hoặc `/scan_normalized`
- Fixed Frame: dùng `odom` nếu chưa có SLAM, dùng `map` nếu chạy SLAM

Nếu RViz báo lỗi transform, kiểm tra:

```bash
ros2 run tf2_tools view_frames
```

### Kiểm tra camera RGB

Trước tiên tìm topic thực tế:

```bash
ros2 topic list | grep camera
```

Các topic có thể gặp:

```text
/camera/image_raw
/camera/image_raw/image_color
```

Kiểm tra:

```bash
ros2 topic hz /camera/image_raw/image_color
ros2 topic echo /camera/image_raw/image_color
```

Nếu có `rqt_image_view`:

```bash
ros2 run rqt_image_view rqt_image_view
```

Nếu máy chưa có:

```bash
sudo apt install ros-jazzy-rqt-image-view
```

### Kiểm tra depth camera

Tìm topic:

```bash
ros2 topic list | grep depth
```

Các topic có thể gặp:

```text
/depth_camera/image_depth
/depth_camera/image_depth/image
```

Kiểm tra:

```bash
ros2 topic hz /depth_camera/image_depth/image
ros2 topic echo /depth_camera/image_depth/image
```

### Ý nghĩa RGB + depth

- Camera RGB cho biết vật thể nào đang nằm trong ảnh.
- Depth camera cho biết khoảng cách từ camera đến vật thể.
- Khi kết hợp RGB + depth, robot có thể ước lượng vị trí rác trong không gian, thay vì chỉ biết bounding box 2D trên ảnh.
- `trash_localization_node.py` lấy tâm bounding box, đọc median depth xung quanh tâm, rồi biến đổi điểm từ `camera_link` sang `map` bằng TF.

---

## 12. Hướng dẫn RViz

Mở RViz trống:

```bash
rviz2
```

Mở RViz theo config SLAM của dự án:

```bash
cd ~/Truong_STU/CleanRobot_STU/clean_robot_ws
source install/setup.bash
ros2 launch clean_robot_navigation rviz.launch.py
```

Config `clean_robot_navigation/rviz/slam.rviz` hiện có:

| Display | Topic/Frame |
|---|---|
| Grid | Fixed Frame |
| Map | `/map` |
| LaserScan | `/scan_normalized` |
| RobotModel | `/robot_description` |
| TF | `map`, `odom`, `base_footprint`, `base_link`, `camera_link`, `lidar_link`, wheel links |

### Display nên thêm khi debug

- `TF`
- `RobotModel`
- `LaserScan`
- `Odometry`
- `Image`
- `Map` nếu chạy SLAM
- `Path` nếu chạy Nav2

### Fixed Frame là gì?

Fixed Frame là frame gốc để RViz vẽ mọi thứ.

Gợi ý:

| Tình huống | Fixed Frame nên dùng |
|---|---|
| Chỉ chạy simulation, chưa có SLAM | `odom` |
| Đang chạy SLAM | `map` |
| RViz báo lỗi frame `map` không tồn tại | Chuyển sang `odom` hoặc chạy SLAM/map server. |

Nếu RViz không hiện LaserScan:

- Kiểm tra `/scan` hoặc `/scan_normalized`.
- Kiểm tra Fixed Frame.
- Kiểm tra TF từ Fixed Frame tới `lidar_link`.

---

## 13. Hướng dẫn SLAM

Dự án đã có cấu hình SLAM bằng `slam_toolbox`.

### File liên quan

| File | Vai trò |
|---|---|
| `clean_robot_navigation/launch/slam.launch.py` | Launch scan normalizer + `async_slam_toolbox_node`. |
| `clean_robot_navigation/launch/mapping.launch.py` | Launch simulation + SLAM. |
| `clean_robot_navigation/config/slam_params.yaml` | Tham số SLAM chính. |
| `clean_robot_navigation/scripts/scan_normalizer_node.py` | Chuẩn hóa `/scan` sang `/scan_normalized`. |
| `clean_robot_navigation/rviz/slam.rviz` | RViz config để xem map. |

### Chạy simulation + SLAM

```bash
cd ~/Truong_STU/CleanRobot_STU/clean_robot_ws
source install/setup.bash
ros2 launch clean_robot_navigation mapping.launch.py
```

Mở RViz:

```bash
ros2 launch clean_robot_navigation rviz.launch.py
```

### Chỉ chạy SLAM khi simulation đã chạy

```bash
ros2 launch clean_robot_navigation slam.launch.py
```

### Điều kiện để SLAM chạy được

| Điều kiện | Cách kiểm tra |
|---|---|
| Có `/scan` từ Webots | `ros2 topic hz /scan` |
| Có `/scan_normalized` | `ros2 topic hz /scan_normalized` |
| Có `/odom` | `ros2 topic hz /odom` |
| Có TF `odom -> base_footprint` | `ros2 run tf2_tools view_frames` |
| Có TF `base_link -> lidar_link` | Xem RViz TF hoặc `view_frames`. |
| Có `/clock` khi dùng sim time | `ros2 topic echo /clock` |
| Robot di chuyển | Publish `/cmd_vel` hoặc `/robot/manual_cmd`. |

### Kiểm tra SLAM lifecycle

```bash
ros2 lifecycle get /slam_toolbox
```

Nếu node chưa active, xem log của `slam.launch.py`. Launch hiện có cơ chế tự configure và activate nếu `autostart=true`.

### Kiểm tra map

```bash
ros2 topic echo /map
ros2 topic hz /map
```

Trong RViz, Fixed Frame nên là `map`, display Map dùng `/map`.

### Lưu map

Khi SLAM đã tạo map tốt:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/Truong_STU/CleanRobot_STU/clean_robot_ws/src/clean_robot_navigation/maps/my_map
```

Sau đó build lại để map được copy sang `install/`:

```bash
colcon build --packages-select clean_robot_navigation
source install/setup.bash
```

---

## 14. Hướng dẫn Nav2

Dự án đã có cấu hình Nav2 trong `clean_robot_navigation/config/nav2_params.yaml` và launch:

```text
clean_robot_navigation/launch/nav2.launch.py
```

### Thành phần Nav2 được cấu hình

Trong `nav2_params.yaml` có cấu hình cho:

| Thành phần | Vai trò |
|---|---|
| `amcl` | Định vị trên map tĩnh. Có tham số, nhưng launch hiện tại chưa khởi động localization riêng. |
| `bt_navigator` | Nhận action `navigate_to_pose`, chạy behavior tree. |
| `controller_server` | Bám path, publish velocity. |
| `planner_server` | Tạo path global. |
| `smoother_server` | Làm mượt path. |
| `behavior_server` | Spin, backup, drive_on_heading, wait. |
| `waypoint_follower` | Theo waypoint. |
| `velocity_smoother` | Làm mượt `/cmd_vel`. |
| `collision_monitor` | Giám sát va chạm, output `/cmd_vel`. |
| `local_costmap` | Costmap cục bộ, dùng `/scan`. |
| `global_costmap` | Costmap toàn cục, dùng map và `/scan`. |

### Chạy Nav2 với SLAM online

Terminal 1: chạy simulation.

```bash
cd ~/Truong_STU/CleanRobot_STU/clean_robot_ws
source install/setup.bash
ros2 launch clean_robot_simulation robot_launch.py
```

Terminal 2: chạy SLAM.

```bash
source ~/Truong_STU/CleanRobot_STU/clean_robot_ws/install/setup.bash
ros2 launch clean_robot_navigation slam.launch.py
```

Terminal 3: chạy Nav2.

```bash
source ~/Truong_STU/CleanRobot_STU/clean_robot_ws/install/setup.bash
ros2 launch clean_robot_navigation nav2.launch.py
```

Terminal 4: mở RViz.

```bash
source ~/Truong_STU/CleanRobot_STU/clean_robot_ws/install/setup.bash
ros2 launch clean_robot_navigation rviz.launch.py
```

### Chạy Nav2 với static map

Source hiện có `maps/my_map.yaml`, nhưng chưa thấy launch riêng khởi động `map_server` + `amcl` với file này. Đây là phần **cần bổ sung/kiểm chứng**.

Hướng đi đề xuất:

- Tạo launch mới include `nav2_bringup/localization_launch.py` với `map:=.../my_map.yaml`.
- Sau đó chạy `nav2.launch.py`.
- Hoặc chuyển `nav2.launch.py` sang `nav2_bringup/bringup_launch.py` nếu muốn bringup đầy đủ map server + localization + navigation.

### Điều kiện để Nav2 chạy

| Điều kiện | Cách kiểm tra |
|---|---|
| Robot nhận `/cmd_vel` | Publish test `/cmd_vel`, xem robot di chuyển. |
| Có `/odom` | `ros2 topic hz /odom` |
| Có `/tf` đúng | `ros2 run tf2_tools view_frames` |
| Có map hoặc SLAM | `ros2 topic echo /map` |
| Có LiDAR `/scan` | `ros2 topic hz /scan` |
| Có `/clock` khi simulation | `ros2 topic echo /clock` |
| Nav2 action server sẵn sàng | `ros2 action list`, `ros2 action info /navigate_to_pose` |

### Gửi goal bằng RViz

Trong RViz:

1. Fixed Frame: `map`.
2. Chờ map/TF hiển thị đúng.
3. Dùng tool `2D Goal Pose` hoặc `Nav2 Goal` tùy plugin.
4. Click vị trí goal trên map.

### Gửi goal bằng command line

Mission package gửi action `navigate_to_pose`. Người mới thường dùng RViz dễ hơn. Nếu cần test bằng command line, có thể dùng action:

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{
  pose: {
    header: {frame_id: 'map'},
    pose: {
      position: {x: 1.0, y: 0.0, z: 0.0},
      orientation: {w: 1.0}
    }
  }
}"
```

---

## 15. Debug lỗi thường gặp

| Lỗi | Nguyên nhân có thể | Cách kiểm tra | Cách sửa |
|---|---|---|---|
| Robot không di chuyển | Chưa publish `/cmd_vel`; driver chưa subscribe `/cmd_vel`; tên motor trong Webots sai; tên robot trong Webots không khớp launch; Webots controller chưa kết nối; wheel velocity bằng 0; sai entry point trong `setup.py`. | `ros2 topic echo /cmd_vel`; `ros2 node list`; `ros2 topic info /cmd_vel`; xem log `robot_launch.py`. | Chạy `robot_launch.py`; kiểm tra `robot_name='my_robot'`; kiểm tra `.wbt` có `left wheel motor`, `right wheel motor`; publish `/robot/manual_cmd STOP` rồi `FORWARD`; build/source lại. |
| `/odom` không nhảy số | Robot chưa di chuyển; driver chưa publish odometry; sai thời gian simulation; thiếu `/clock`; chưa update encoder/wheel position; GPS/IMU không có. | `ros2 topic echo /odom`; `ros2 topic hz /odom`; `ros2 topic echo /clock`; xem log driver báo Encoder/Ground truth. | Kiểm tra `/cmd_vel`; kiểm tra device `gps`, `inertial_unit`, wheel sensors trong `.wbt`; chạy lại simulation. |
| RViz không hiện LaserScan | Không có `/scan`; sai Fixed Frame; thiếu TF từ base tới `lidar_link`; LiDAR/Webots device chưa map đúng. | `ros2 topic list | grep scan`; `ros2 topic hz /scan`; `ros2 run tf2_tools view_frames`. | Chọn Fixed Frame `odom` hoặc `map`; sửa device reference `lidar`; chạy `robot_state_publisher`; kiểm tra xacro và `.wbt`. |
| SLAM không tạo map | Không có `/scan`; không có `/scan_normalized`; không có `/tf`; không có `/odom`; robot đứng yên; sai `use_sim_time`; `/clock` không chạy. | `ros2 topic hz /scan`; `ros2 topic hz /scan_normalized`; `ros2 topic hz /odom`; `ros2 topic echo /clock`; `ros2 lifecycle get /slam_toolbox`. | Chạy `mapping.launch.py`; điều khiển robot di chuyển; kiểm tra frame `odom`, `base_footprint`, `lidar_link`; sửa topic scan. |
| Webots báo waiting for extern controller | Webots đang chờ ROS2/Webots controller kết nối vào robot. | Kiểm tra `.wbt`: `name "my_robot"`, `controller "<extern>"`; kiểm tra `robot_launch.py`: `robot_name='my_robot'`. | Đảm bảo đã chạy `ros2 launch clean_robot_simulation robot_launch.py`; tên robot trong `.wbt` và launch phải khớp; kiểm tra `webots_ros2_driver`. |
| `/clock` không có | Webots/supervisor chưa chạy hoặc launch lỗi. | `ros2 topic list | grep clock`; `ros2 topic echo /clock`. | Chạy lại `robot_launch.py`; kiểm tra Webots có mở thành công. |
| Camera không có ảnh | Topic sai; device name không khớp; Webots camera chưa publish; perception subscribe sai topic. | `ros2 topic list | grep camera`; `ros2 topic hz <topic>`. | Sửa `image_topic` hoặc xacro mapping; kiểm tra device `rgb_camera`. |
| Depth không có ảnh | Topic sai; RangeFinder chưa publish; perception subscribe sai topic. | `ros2 topic list | grep depth`; `ros2 topic hz <topic>`. | Sửa `depth_topic`; kiểm tra device `depth_camera`. |
| Perception không detect | Chưa cài `ultralytics`; thiếu model `yolov8n.pt`; ảnh không vào node; class filter không khớp. | Xem log detector; `ros2 topic hz /trash/detections`; kiểm tra topic ảnh. | Cài dependency; đặt đúng `model_path`; kiểm tra camera; sửa `target_classes`. |
| Localization không publish candidate | Không có depth; không transform được `camera_link -> map`; depth ngoài range. | `ros2 topic echo /trash/detections`; `ros2 topic echo /depth_camera/image_depth/image`; log localization. | Chạy SLAM để có `map`; đổi `target_frame` sang `odom` khi test; sửa topic depth. |
| Mission báo Nav2 action server chưa ready | Nav2 chưa chạy hoặc lifecycle chưa active. | `ros2 action list`; `ros2 action info /navigate_to_pose`; xem log Nav2. | Chạy `nav2.launch.py`; đảm bảo map/TF/odom/scan đủ. |
| Nav2 không publish `/cmd_vel` | Chưa có map; costmap lỗi; goal invalid; action server chưa active; collision monitor chặn. | `ros2 topic echo /cmd_vel`; `ros2 action info /navigate_to_pose`; xem log controller/planner. | Kiểm tra `/map`, `/tf`, `/odom`, `/scan`; gửi goal trong vùng map. |
| Build xong nhưng chạy code cũ | Chưa source `install/setup.bash`; đang mở terminal cũ; sửa file trong `src` nhưng chưa build. | `which ros2`; `ros2 pkg prefix <package>`; xem log. | `colcon build`, sau đó `source install/setup.bash` trong terminal đang chạy. |

---

## 16. Quy trình làm việc cho thành viên mới

1. Clone source về máy.

```bash
cd ~/Truong_STU
git clone <repo-url> CleanRobot_STU
```

2. Source ROS2.

```bash
source /opt/ros/jazzy/setup.bash
```

3. Cài dependency.

```bash
cd ~/Truong_STU/CleanRobot_STU/clean_robot_ws
rosdep install --from-paths src --ignore-src -r -y
```

4. Build workspace.

```bash
colcon build
source install/setup.bash
```

5. Kiểm tra package.

```bash
ros2 pkg list | grep clean_robot
```

6. Chạy mô phỏng Webots.

```bash
ros2 launch clean_robot_simulation robot_launch.py
```

7. Kiểm tra topic cơ bản.

```bash
ros2 topic list
ros2 topic echo /clock
ros2 topic echo /odom
ros2 topic echo /tf
ros2 topic echo /scan
```

8. Điều khiển robot.

```bash
ros2 topic pub --once /robot/manual_cmd std_msgs/msg/String "{data: 'FORWARD'}"
ros2 topic pub --once /robot/manual_cmd std_msgs/msg/String "{data: 'STOP'}"
```

9. Mở RViz.

```bash
ros2 launch clean_robot_navigation rviz.launch.py
```

10. Chạy SLAM nếu cần.

```bash
ros2 launch clean_robot_navigation slam.launch.py
```

11. Chạy perception nếu camera/depth đã có topic.

```bash
ros2 launch clean_robot_perception perception.launch.py
```

12. Chạy Nav2.

```bash
ros2 launch clean_robot_navigation nav2.launch.py
```

13. Chạy mission.

```bash
ros2 launch clean_robot_mission mission.launch.py
```

14. Bắt đầu sửa package được phân công. Trước khi sửa, đọc:

- `package.xml`
- `setup.py` hoặc `CMakeLists.txt`
- `launch/*.py`
- node Python liên quan
- message custom nếu dùng

15. Sau khi sửa, build và source lại.

```bash
colcon build --packages-select <ten_package>
source install/setup.bash
```

---

## 17. Phân công module

Phân công theo cấu trúc hiện tại:

| Package | Vai trò | Người/phần phụ trách theo README/AGENTS |
|---|---|---|
| `clean_robot_msgs` | Định nghĩa message chung: detection, candidate, pose rác, trạng thái. | Duy Khang |
| `clean_robot_description` | URDF/Xacro, frame, robot model, sensor mount. | Duy Khang |
| `clean_robot_simulation` | Webots, driver, sensor, odom, TF, manual control. | Hoài |
| `clean_robot_perception` | Nhận diện rác bằng camera/depth, tạo candidate. | Khải |
| `clean_robot_navigation` | SLAM, Nav2, map, costmap, RViz navigation. | Khang, Khải |
| `clean_robot_mission` | Logic nhiệm vụ tổng thể: tìm rác, đi tới rác, xử lý target. | Khải |

Nguyên tắc làm việc:

- Mỗi người làm trong package của mình để tránh đụng code không cần thiết.
- Các package phải thống nhất topic, frame và message.
- Nếu đổi message trong `clean_robot_msgs`, phải thông báo vì perception/mission có thể bị ảnh hưởng.
- Nếu đổi frame trong URDF, phải kiểm tra lại SLAM/Nav2/RViz/perception TF.
- Nếu đổi topic sensor trong Webots/Xacro, phải sửa perception/navigation tương ứng.

---

## 18. Chuẩn đặt tên topic/frame

### Topic chuẩn nên dùng trong dự án

Nên ưu tiên giữ topic đang có trong source để giảm lỗi tích hợp:

| Topic | Trạng thái hiện tại | Vai trò |
|---|---|---|
| `/cmd_vel` | Đang dùng | Lệnh vận tốc chuẩn. |
| `/robot/manual_cmd` | Đang dùng | Lệnh chữ để test. |
| `/odom` | Đang dùng | Odometry. |
| `/tf` | Đang dùng | TF động. |
| `/tf_static` | Dự kiến từ robot_state_publisher | TF cố định. |
| `/joint_states` | Đang dùng | Joint state bánh xe. |
| `/scan` | Đang dùng | LiDAR gốc. |
| `/scan_normalized` | Đang dùng cho SLAM | LiDAR đã chuẩn hóa. |
| `/camera/image_raw` | Khai báo trong xacro | Topic RGB gốc từ Webots. |
| `/camera/image_raw/image_color` | Perception đang subscribe mặc định | Topic RGB thực tế cần kiểm tra bằng `ros2 topic list`. |
| `/depth_camera/image_depth` | Khai báo trong xacro | Topic depth gốc từ Webots. |
| `/depth_camera/image_depth/image` | Perception đang subscribe mặc định | Topic depth thực tế cần kiểm tra bằng `ros2 topic list`. |
| `/trash/detections` | Đang dùng | Detection 2D. |
| `/trash/candidates` | Đang dùng | Candidate rác có pose. |
| `/trash/tracked_candidates` | Đang dùng | Candidate ổn định. |
| `/trash/target_pose` | Đang dùng | Target pose cho mission/Nav2. |
| `/trash/target_id` | Đang dùng | ID target. |
| `/trash/rejected_id` | Đang dùng | Target bị reject/fail. |
| `/mission/state` | Đang dùng | Trạng thái mission. |
| `/mission/event` | Đang dùng | Event mission. |

Không nên đổi sang `/trash_detections` hoặc `/trash_target` nếu không refactor toàn bộ code, vì source hiện dùng namespace `/trash/...`.

### Frame chuẩn nên dùng

Frame hiện tại trong URDF/RViz:

| Frame | Vai trò |
|---|---|
| `map` | Frame bản đồ do SLAM hoặc map server tạo. |
| `odom` | Frame odometry cục bộ, liên tục nhưng có thể trôi. |
| `base_footprint` | Gốc robot trên mặt phẳng, child của `odom`. |
| `base_link` | Thân robot, child của `base_footprint`. |
| `lidar_link` | Frame LiDAR hiện đang dùng trong URDF. |
| `camera_link` | Frame camera RGB/depth hiện đang dùng. |
| `left_wheel_link` | Link bánh trái. |
| `right_wheel_link` | Link bánh phải. |

Một số tài liệu ROS hay dùng `laser_link`. Source hiện tại dùng `lidar_link`. Nếu nhóm muốn đổi sang `laser_link`, phải đổi đồng bộ:

- `sensors.urdf.xacro`
- `clean_robot.urdf.xacro`
- RViz config
- SLAM/Nav2 nếu có frame hard-code
- perception nếu có dùng frame sensor

### Vai trò từng frame

```text
map
└── odom
    └── base_footprint
        └── base_link
            ├── lidar_link
            ├── camera_link
            ├── left_wheel_link
            └── right_wheel_link
```

- `map -> odom`: thường do SLAM/AMCL publish.
- `odom -> base_footprint`: driver publish.
- `base_footprint -> base_link`: URDF/robot_state_publisher publish.
- `base_link -> sensors/wheels`: URDF/robot_state_publisher publish.

---

## 19. Lộ trình phát triển tiếp theo

### Phase 1: Robot chạy được trong Webots

Mục tiêu:

- Robot nhận `/cmd_vel`.
- Robot publish `/odom`.
- Robot publish `/tf`.
- Robot publish `/joint_states`.
- Webots publish `/clock`.
- Kiểm tra sensor `/scan`, camera RGB, depth camera.

Trạng thái hiện tại: **Đã có code**, cần kiểm tra lại đầy đủ sau mỗi lần thay đổi world/URDF.

### Phase 2: SLAM

Mục tiêu:

- LiDAR `/scan` ổn định.
- `/scan_normalized` ổn định.
- TF đúng: `odom`, `base_footprint`, `lidar_link`.
- Chạy `slam_toolbox`.
- Hiển thị `/map` trong RViz.
- Lưu map ra `maps/`.

Trạng thái hiện tại: **Đã có cấu hình và launch**, cần kiểm thử bản đồ thực tế.

### Phase 3: Nav2

Mục tiêu:

- Robot đi tới goal trong map.
- Costmap local/global hoạt động.
- Planner/controller ổn định với robot nhỏ.
- Nav2 publish `/cmd_vel` hợp lý.
- Có launch rõ cho chế độ SLAM online và static map.

Trạng thái hiện tại: **Đã có config**, nhưng static map + AMCL launch còn **cần bổ sung/kiểm chứng**.

### Phase 4: Perception

Mục tiêu:

- Camera RGB nhận diện rác trong Webots.
- Depth camera ước lượng khoảng cách.
- Xuất `/trash/detections`.
- Xuất `/trash/candidates`.
- Xuất `/trash/tracked_candidates`.
- Pose rác đúng frame `map` hoặc `odom`.

Trạng thái hiện tại: **Đã có code pipeline**, cần kiểm tra dependency YOLO, topic camera/depth, TF `camera_link -> map`.

### Phase 5: Mission

Mục tiêu:

- Tìm rác.
- Chọn target tốt nhất.
- Đi tới rác.
- Nhặt rác.
- Đi tới điểm thả.
- Thả rác.
- Xử lý fail/retry.

Trạng thái hiện tại: **Đã có skeleton mission + Nav2 goal**, phần nhặt/thả rác **chưa hoàn thiện**.

---

## 20. Phụ lục lệnh ROS2 thường dùng

### Topic

Liệt kê topic:

```bash
ros2 topic list
```

Xem dữ liệu topic:

```bash
ros2 topic echo /topic_name
```

Xem tần số publish:

```bash
ros2 topic hz /topic_name
```

Xem thông tin topic:

```bash
ros2 topic info /topic_name
```

Publish một lệnh `/cmd_vel`:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.15}, angular: {z: 0.0}}"
```

### Node

Liệt kê node:

```bash
ros2 node list
```

Xem thông tin node:

```bash
ros2 node info /node_name
```

### Interface

Xem cấu trúc message:

```bash
ros2 interface show geometry_msgs/msg/Twist
ros2 interface show nav_msgs/msg/Odometry
ros2 interface show sensor_msgs/msg/LaserScan
ros2 interface show clean_robot_msgs/msg/TrashCandidate
```

### Run executable

```bash
ros2 run package_name executable_name
```

Ví dụ:

```bash
ros2 run clean_robot_perception fake_trash_candidate_node
```

### Launch

```bash
ros2 launch package_name launch_file.py
```

Ví dụ:

```bash
ros2 launch clean_robot_simulation robot_launch.py
ros2 launch clean_robot_navigation slam.launch.py
ros2 launch clean_robot_navigation nav2.launch.py
ros2 launch clean_robot_perception perception.launch.py
ros2 launch clean_robot_mission mission.launch.py
```

### Build

Build toàn workspace:

```bash
colcon build
```

Build một package:

```bash
colcon build --packages-select package_name
```

Source workspace:

```bash
source install/setup.bash
```

### TF

Tạo sơ đồ TF:

```bash
ros2 run tf2_tools view_frames
```

Xem transform giữa hai frame:

```bash
ros2 run tf2_ros tf2_echo odom base_footprint
ros2 run tf2_ros tf2_echo base_link lidar_link
ros2 run tf2_ros tf2_echo base_link camera_link
```

### Action

Liệt kê action:

```bash
ros2 action list
```

Xem action Nav2:

```bash
ros2 action info /navigate_to_pose
```

Gửi goal Nav2:

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{
  pose: {
    header: {frame_id: 'map'},
    pose: {
      position: {x: 1.0, y: 0.0, z: 0.0},
      orientation: {w: 1.0}
    }
  }
}"
```

### Lifecycle

Kiểm tra lifecycle node:

```bash
ros2 lifecycle get /slam_toolbox
```

### Các lệnh kiểm tra nhanh theo dự án

```bash
ros2 topic echo /clock
ros2 topic echo /odom
ros2 topic echo /scan
ros2 topic echo /scan_normalized
ros2 topic echo /trash/detections
ros2 topic echo /trash/candidates
ros2 topic echo /trash/tracked_candidates
ros2 topic echo /mission/state
```

---

## 21. Kết luận

Hiện tại dự án Clean Robot tập trung vào mô phỏng Webots, điều khiển robot bằng ROS2, sensor, odometry và TF. Đây là nền tảng bắt buộc trước khi SLAM, Nav2, perception và mission chạy ổn định.

Muốn SLAM/Nav2 ổn thì phải làm chắc simulation trước:

- `/cmd_vel` điều khiển robot đúng.
- `/odom` thay đổi đúng khi robot chạy.
- `/tf` đầy đủ và không sai frame.
- `/scan` có dữ liệu hợp lệ.
- `/clock` chạy khi dùng `use_sim_time`.

Không nên nhảy ngay vào AI nhận diện rác nếu robot chưa publish đúng `/scan`, `/odom`, `/tf` và `/clock`. Perception và mission chỉ hoạt động tốt khi nền tảng mô phỏng, frame và topic đã ổn định.

Tài liệu này là tài liệu nền để thành viên mới hiểu hệ thống, build được workspace, chạy được mô phỏng, kiểm tra topic, và debug các lỗi cơ bản trong quá trình phát triển Clean Robot.
