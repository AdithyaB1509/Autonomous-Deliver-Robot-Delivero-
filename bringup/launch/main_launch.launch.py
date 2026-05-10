#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # --- 1. PATH SETUP ---
    pkg_bringup = get_package_share_directory('bringup')
    pkg_sllidar_ros = get_package_share_directory('sllidar_ros2') 
    pkg_imu = get_package_share_directory('imu_bno055_node')
    pkg_rf2o = get_package_share_directory('rf2o_laser_odometry')
    
    ekf_config_path = os.path.join(pkg_bringup, 'config', 'ekf_config.yaml')
    laser_filter_config_path = os.path.join(pkg_bringup, 'config', 'laser_filter.yaml')

    # --- 2. HARDWARE NODES ---
    sllidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_sllidar_ros, 'launch', 'sllidar_a1_launch.py')),
        launch_arguments={
            'serial_port': '/dev/ttyUSB0',
            'frame_id': 'laser',
            'inverted': 'false',
            'angle_compensate': 'true'
        }.items()
    )

    laser_filter_node = Node(
        package='laser_filters',
        executable='scan_to_scan_filter_chain',
        name='laser_filter',
        parameters=[laser_filter_config_path],
        remappings=[
            ('scan', 'scan_unfiltered'),
            ('scan_filtered', 'scan')
        ]
    )

    imu_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_imu, 'launch', 'fullimu.launch.py'))
    )

    rf2o_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_rf2o, 'launch', 'rf2o_laser_odometry.launch.py'))
    )

    esp32_bridge_node = Node(
        package='esp32_bridge', 
        executable='bridge_node', 
        name='esp32_bridge', 
        output='screen'
    )

    # --- 3. TRANSFORMS & FUSION ---
    ekf_node = Node(
        package='robot_localization', 
        executable='ekf_node', 
        name='ekf_filter_node',
        output='screen', 
        parameters=[ekf_config_path, {'use_sim_time': False}]
    )   

    static_tf_laser = Node(
        package='tf2_ros', 
        executable='static_transform_publisher', 
        name='static_tf_pub_laser',
        arguments=['0.1', '0', '0.2', '0', '0', '0', 'base_link', 'laser']
    )

    static_tf_imu = Node(
        package='tf2_ros', 
        executable='static_transform_publisher', 
        name='static_tf_pub_imu',
        arguments=['0', '0', '0.1', '0', '0', '0', 'base_link', 'imu_link']
    )

    # --- 4. MADGWICK FILTER ---
    madgwick_node = Node(
        package='imu_filter_madgwick',
        executable='imu_filter_madgwick_node',
        name='imu_filter_madgwick',
        output='screen',
        respawn=True,
        respawn_delay=2.0,
        parameters=[{
            'use_mag': False,
            'publish_tf': False,
            'world_frame': 'enu',
            'fixed_frame': 'odom',
            'gain': 0.1,
        }],
        remappings=[
            ('/imu/data_raw', '/imu/data_raw'),
            ('/imu/mag',      '/imu/mag')
        ]
    )

    # --- 5. RETURN DESCRIPTION ---
    return LaunchDescription([
        # Layer 1 — Hardware & Transforms
        static_tf_laser,
        static_tf_imu,
        sllidar_launch,
        laser_filter_node,
        imu_launch,
        esp32_bridge_node,
        madgwick_node,

        # Layer 2 — Odometry (Needs Lidar + IMU ready)
        TimerAction(
            period=3.0,
            actions=[rf2o_launch]
        ),

        # Layer 3 — EKF Fusion (Needs rf2o odom ready)
        TimerAction(
            period=5.0,
            actions=[ekf_node]
        ),
    ])