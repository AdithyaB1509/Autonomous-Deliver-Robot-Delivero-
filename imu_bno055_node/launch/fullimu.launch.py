import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    
    # 1. Point to the correct package name: imu_bno055_node
    pkg_name = 'imu_bno055_node'
    
    # 2. Correct the path to your config file
    default_config = os.path.join(
        get_package_share_directory(pkg_name), 'config', 'bno055_config.yaml'
    )
    
    return LaunchDescription([
        # 1. IMU DRIVER
        Node(
            package=pkg_name,      # Updated from 'myimu'
            executable='imupub',   # Matches your setup.py entry_point
            name='imu_hardware_driver',
            output='screen',
            emulate_tty=True,
            respawn=True,     
            respawn_delay=2.0,
            parameters=[default_config] # Pass the YAML file directly
        ),

        # 2. MADGWICK FILTER
        Node(
            package='imu_filter_madgwick',
            executable='imu_filter_madgwick_node',
            name='imu_filter',
            output='screen',
            respawn=True,
            respawn_delay=1.0,
            parameters=[{
                'use_mag': True,
                'publish_tf': False, 
                'world_frame': 'enu',
                'fixed_frame': 'odom',
            }]
        )
    ])