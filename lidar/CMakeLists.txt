cmake_minimum_required(VERSION 3.8)
project(lidar)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_srvs REQUIRED)

set(delta_lidar_SDK_PATH "./sdk/")

FILE(GLOB delta_lidar_SDK_SRC 
  "${delta_lidar_SDK_PATH}/src/*.cpp"
)

include_directories(
  ${delta_lidar_SDK_PATH}/include
  ${delta_lidar_SDK_PATH}/src
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

add_executable(delta_lidar_node src/node.cpp ${delta_lidar_SDK_SRC})
target_link_libraries(delta_lidar_node)
ament_target_dependencies(delta_lidar_node 
  rclcpp 
  sensor_msgs
  std_srvs)
add_executable(delta_lidar_node_client src/client.cpp)
target_link_libraries(delta_lidar_node_client)
ament_target_dependencies(delta_lidar_node_client 
  rclcpp 
  sensor_msgs
  std_srvs)
install(TARGETS delta_lidar_node delta_lidar_node_client
  ARCHIVE DESTINATION lib/${PROJECT_NAME}
  LIBRARY DESTINATION lib/${PROJECT_NAME}
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch sdk
  DESTINATION share/${PROJECT_NAME}
  USE_SOURCE_PERMISSIONS
)
ament_package()