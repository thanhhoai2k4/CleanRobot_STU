cmake_minimum_required(VERSION 3.8)
project(clean_robot_navigation)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

# Đóng gói các thư mục tài nguyên sang share/
install(
  DIRECTORY config launch maps rviz
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS scripts/scan_normalizer_node.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
