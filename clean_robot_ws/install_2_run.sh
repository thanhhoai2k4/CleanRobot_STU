 

colcon build  --packages-select clean_robot_simulation
source install/setup.sh
ros2 run clean_robot_simulation simulation_test_node