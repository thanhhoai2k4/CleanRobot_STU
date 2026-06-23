cmake_minimum_required(VERSION 3.8)
project(clean_robot_msgs)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Tìm các thư viện phụ thuộc
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

# Khai báo các file msg cần biên dịch
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/TrashDetection2D.msg"
  "msg/TrashDetection2DArray.msg"
  "msg/TrashCandidate.msg"
  "msg/TrashCandidateArray.msg"
  DEPENDENCIES std_msgs geometry_msgs
)

ament_package()