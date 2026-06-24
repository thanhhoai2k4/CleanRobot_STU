# CleanRobot_STU Project Workspace (Context & Directory Layout)

Tài liệu này cung cấp ngữ cảnh chung về toàn bộ dự án robot và vai trò của các package cho AI Agent (Antigravity).

## 1. Giới thiệu Dự án
Dự án **CleanRobot_STU** là một hệ thống robot dọn rác tự động được phát triển trên ROS 2 Jazzy Jalisco và mô phỏng thông qua Webots simulator trên hệ điều hành Ubuntu 24.04 LTS.

## 2. Phân chia vai trò của các Package trong `clean_robot_ws/src/`
- **`clean_robot_msgs`** (Duy Khang phụ trách): Nơi lưu trữ trạng thái, custom message, service dùng chung cho toàn bộ robot (ví dụ: tọa độ x, y, z, độ tin cậy confident,...).
- **`clean_robot_description`** (Duy Khang phụ trách): Package chứa file mô tả hình học URDF của xe, cấu hình 3D hiển thị trên RViz2 và các launch file khởi tạo cấu trúc robot.
- **`clean_robot_perception`** (Khải phụ trách): Nhận dữ liệu camera/lidar và chạy các thuật toán thị giác máy tính nhận diện rác.
- **`clean_robot_mission`** (Khải phụ trách): Package lõi điều phối nhiệm vụ (Mission Control). Quản lý logic:
  - Nếu chưa thấy rác -> điều khiển đi tuần tra/tìm rác.
  - Nếu phát hiện rác -> gửi tọa độ mục tiêu (Goal) cho Nav2.
  - Nếu đã đến vị trí rác -> kích hoạt dọn rác và dừng/chuyển tiếp nhiệm vụ.
- **`clean_robot_navigation`** (Khang, Khải phụ trách): Chứa cấu hình Nav2 (Navigation 2), SLAM (vẽ bản đồ), AMCL (định vị) và bản đồ môi trường.
- **`clean_robot_simulation`** (Hoài phụ trách): Chứa các node điều khiển kết nối trực tiếp với simulator Webots để xe chạy và phản hồi dữ liệu trong môi trường ảo.

## 3. Kiến trúc luồng dữ liệu (Dataflow)
- **Manual Control / Mission Node** -> gửi vận tốc `geometry_msgs/msg/Twist` qua topic `/cmd_vel` -> Webots driver nhận và điều khiển động cơ robot chạy.
- **Phản hồi từ robot:** Cảm biến camera publish ảnh qua `/camera/image_raw`, Lidar truyền dữ liệu qua `/scan`, tọa độ ước lượng của xe publish qua `/odom`.
