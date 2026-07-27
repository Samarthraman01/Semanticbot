cmake_minimum_required(VERSION 3.8)
project(segformer_inference)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(OpenCV REQUIRED)
# ONNX Runtime
set(ONNXRUNTIME_ROOT /opt/onnxruntime)
include_directories(${ONNXRUNTIME_ROOT}/include)
link_directories(${ONNXRUNTIME_ROOT}/lib)

add_executable(inference_node src/inference_node.cpp)

ament_target_dependencies(inference_node
    rclcpp
    sensor_msgs
    cv_bridge
    OpenCV
)
target_link_libraries(inference_node
    onnxruntime
)

install(TARGETS inference_node
    DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()