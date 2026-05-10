#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # ==========================================
    # 1. ARGS & CONFIGURATION
    # ==========================================
    channel_type = LaunchConfiguration('channel_type', default='serial')
    serial_port = LaunchConfiguration('serial_port', default='/dev/ttyUSB0')
    serial_baudrate = LaunchConfiguration('serial_baudrate', default='115200')
    lidar_frame_id = LaunchConfiguration('lidar_frame_id', default='laser')
    inverted = LaunchConfiguration('inverted', default='false')
    angle_compensate = LaunchConfiguration('angle_compensate', default='true')
    scan_mode = LaunchConfiguration('scan_mode', default='Sensitivity')
    
    pkg_share = get_package_share_directory('bringup')
    ekf_config_path = os.path.join(pkg_share, 'config', 'ekf_config.yaml')
    laser_filter_path = os.path.join(pkg_share, 'config', 'laser_filter.yaml')

    imu_config_path = os.path.join(
        get_package_share_directory('imu_bno055_node'), 'config', 'bno055_config.yaml'
    )

    # ==========================================
    # 2. NODES
    # ==========================================

    # --- A. LIDAR HARDWARE ---
    rplidar_node = Node(
        package='sllidar_ros2',      # Updated package name
        executable='sllidar_node',   # Updated executable name
        name='sllidar_node',
        parameters=[{
            'channel_type': channel_type,
            'serial_port': serial_port,
            'serial_baudrate': serial_baudrate,
            'frame_id': lidar_frame_id,
            'inverted': inverted,
            'angle_compensate': angle_compensate,
            'scan_mode': scan_mode
        }],
        remappings=[('/scan', '/scan_unfiltered')],
        output='screen'
    )

    # --- LASER FILTER NODE (UNCHANGED) ---
    laser_filter_node = Node(
        package='laser_filters',
        executable='scan_to_scan_filter_chain',
        name='laser_filter',
        parameters=[laser_filter_path],
        remappings=[
            ('scan', 'scan_unfiltered'),
            ('scan_filtered', 'scan')
        ],
        output='screen'
    )

    # --- B. IMU HARDWARE (UNCHANGED) ---
    imu_driver_node = Node(
        package='imu_bno055_node',
        executable='imupub',
        name='imu_hardware_driver',
        output='screen',
        emulate_tty=True,
        respawn=True,
        respawn_delay=2.0,
        parameters=[imu_config_path]
    )

    # --- C. TF TRANSFORMS (UNCHANGED) ---
    static_tf_laser = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_laser',
        arguments=['--x', '0.2', '--y', '0.0', '--z', '0.1',
                   '--yaw', '0.0', '--pitch', '0.0', '--roll', '0.0',
                   '--frame-id', 'base_link', '--child-frame-id', 'laser']
    )

    static_tf_imu = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_imu',
        arguments=['--x', '0.0', '--y', '0.0', '--z', '0.0',
                   '--yaw', '0.0', '--pitch', '0.0', '--roll', '0.0',
                   '--frame-id', 'base_link', '--child-frame-id', 'imu_link']
    )

    # --- D. ODOMETRY & FILTERS (UNCHANGED) ---
    rf2o_node = Node(
        package='rf2o_laser_odometry',
        executable='rf2o_laser_odometry_node',
        name='rf2o_laser_odometry',
        output='screen',
        arguments=['--ros-args', '--log-level', 'error'],
        parameters=[{
            'laser_scan_topic': '/scan',
            'odom_topic': '/odom_rf2o',
            'publish_tf': False,
            'base_frame_id': 'base_link',
            'odom_frame_id': 'odom',
            'init_pose_from_topic': '',
            'freq': 10.0
        }],
    )

    # --- E. MOTOR NODE (UPDATED) ---
    motor_node = Node(
        package='esp32_bridge',        # ← was 'glad_motor_controller'
        executable='bridge_node',      # ← matches setup.py entry_point
        name='esp32_bridge',
        output='screen',
        respawn=True,
        respawn_delay=1.0,
        remappings=[('/odom_wheels', '/odom_wheels')]
    )

    # --- F. MADGWICK FILTER (UNCHANGED) ---
    madgwick_node = Node(
        package='imu_filter_madgwick',
        executable='imu_filter_madgwick_node',
        name='imu_filter',
        output='screen',
        respawn=True,
        respawn_delay=1.0,
        parameters=[{
            'use_mag': False,
            'publish_tf': False,
            'world_frame': 'enu',
            'fixed_frame': 'odom',
        }],
        remappings=[
            ('/imu/data_raw', '/imu/data_raw'),
            ('/imu/mag',      '/imu/mag')
        ]
    )

    # --- G. EKF (UNCHANGED) ---
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config_path],
        remappings=[('odometry/filtered', 'odom')]
    )

    # ==========================================
    # 3. BUILD LAUNCH DESCRIPTION (UNCHANGED)
    # ==========================================
    return LaunchDescription([
        DeclareLaunchArgument('channel_type',     default_value='serial'),
        DeclareLaunchArgument('serial_port',      default_value='/dev/ttyUSB0'),
        DeclareLaunchArgument('serial_baudrate',  default_value='115200'),
        DeclareLaunchArgument('lidar_frame_id',   default_value='laser'),
        DeclareLaunchArgument('inverted',         default_value='false'),
        DeclareLaunchArgument('angle_compensate', default_value='true'),
        DeclareLaunchArgument('scan_mode',        default_value='Sensitivity'),

        static_tf_laser,
        static_tf_imu,
        rplidar_node,
        laser_filter_node,
        imu_driver_node,
        madgwick_node,
        motor_node,             # ← now esp32_bridge
        TimerAction(
            period=5.0,
            actions=[rf2o_node, ekf_node]
        ),
    ])