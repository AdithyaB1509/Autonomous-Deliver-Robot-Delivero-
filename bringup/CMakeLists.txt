cmake_minimum_required(VERSION 3.8)
project(bringup)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
# If your GUI uses the custom interfaces, uncomment the line below:
# find_package(delivero_interfaces REQUIRED)

# 1. Install Python scripts to the libexec directory
# This creates the 'lib/bringup' folder that was missing
install(PROGRAMS
  scripts/mission_control_gui.py
  DESTINATION lib/${PROJECT_NAME}
)

# 2. Install launch and config directories to the share directory
install(DIRECTORY 
  launch 
  config
  DESTINATION share/${PROJECT_NAME}
)

# ament_package() MUST be the final line
ament_package()