cmake_minimum_required(VERSION 3.8)
project(semantic_fusion)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(vision_msgs REQUIRED)

add_executable(fusion_node src/fusion_node.cpp)
ament_target_dependencies(fusion_node rclcpp sensor_msgs vision_msgs)

install(TARGETS fusion_node
  DESTINATION lib/${PROJECT_NAME})

ament_package()
