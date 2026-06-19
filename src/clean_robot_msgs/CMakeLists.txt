cmake_minimum_required(VERSION 3.8)
project(clean_robot_msgs)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Tìm các package phụ thuộc bắt buộc
find_package(ament_cmake REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# Khai báo danh sách các file custom message cần build
set(msg_files
  "msg/TrashDetection2D.msg"
  "msg/TrashCandidate.msg"
)

# Lệnh sinh interface của ROS2
rosidl_generate_interfaces(${PROJECT_NAME}
  ${msg_files}
  DEPENDENCIES std_msgs geometry_msgs
)

# Xuất package ra hệ thống
ament_package()