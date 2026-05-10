import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node  # Required to add the GUI node

def generate_launch_description():
    # 1. Get the paths to your package and the official Nav2 package
    bringup_pkg_dir = get_package_share_directory('bringup')
    nav2_bringup_pkg_dir = get_package_share_directory('nav2_bringup')

    # 2. Define the absolute paths to your custom configuration files
    default_map_path = os.path.join(bringup_pkg_dir, 'config', 'robotics_floor.yaml')
    default_params_path = os.path.join(bringup_pkg_dir, 'config', 'nav2_params.yaml')

    # 3. Create Launch Configurations
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    map_yaml_file = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')

    # 4. Declare Launch Arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time', default_value='false', description='Use simulation clock if true')

    declare_autostart_cmd = DeclareLaunchArgument(
        'autostart', default_value='true', description='Automatically startup the nav2 stack')

    declare_map_yaml_cmd = DeclareLaunchArgument(
        'map', default_value=default_map_path, description='Full path to map yaml file to load')

    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file', default_value=default_params_path, description='Full path to the ROS 2 parameters file')

    # 5. Include the official Nav2 bringup launch file
    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_pkg_dir, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': map_yaml_file,
            'use_sim_time': use_sim_time,
            'autostart': autostart,
            'params_file': params_file
        }.items()
    )

    # --- NEW: ADD THE DELIVERO GUI NODE ---
    # --- FIND THIS SECTION IN YOUR navigation.launch.py ---
    mission_control_gui_node = Node(
        package='bringup',
        executable='mission_control_gui.py',  # <--- CHANGE THIS from 'mission_control'
        name='delivero_gui_node',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # 6. Return the Launch Description including the new GUI node
    return LaunchDescription([
        declare_use_sim_time_cmd,
        declare_autostart_cmd,
        declare_map_yaml_cmd,
        declare_params_file_cmd,
        nav2_bringup_launch,
        mission_control_gui_node  # Added GUI node to the execution list
    ])