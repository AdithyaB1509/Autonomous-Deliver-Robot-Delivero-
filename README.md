# Autonomous-Deliver-Robot-Delivero-
A ROS 2 Humble powered autonomous mobile robot (AMR) designed for institutional logistics, featuring SLAM-based mapping, LiDAR navigation, and a custom PyQt5 mission control interface.

Delivero Bot: Autonomous Delivery Ecosystem
Delivero Bot is an intelligent, autonomous mobile robot (AMR) developed for efficient material transport within institutional environments. Built on the ROS 2 Humble framework, the robot utilizes a modular multi-layer architecture to handle perception, navigation, and kinetic execution.

Key Features
Autonomous Navigation: Utilizes the Nav2 stack with Global and Local planners to find the most efficient paths while dodging dynamic obstacles.

High-Precision Localization: Employs AMCL (Adaptive Monte Carlo Localization) and SLAM Toolbox for real-time positioning and environment mapping.

Sensor Fusion: Integrates RPLidar A1 for 360° spatial awareness and the BNO-055 IMU with a Madgwick filter for accurate orientation.

Custom Mission Control: A user-friendly PyQt5-based HMI (Human-Machine Interface) that allows users to send the robot to specific waypoints (C1, C2, etc.) and monitor battery levels in real-time.

Hybrid Control System: Distributed processing between a Raspberry Pi 4 (High-level intelligence) and an ESP32 (Low-level motor control) via a micro-ROS bridge.

Technical Stack
Software: ROS 2 Humble, Python 3, C++, PyQt5, Micro-ROS.

Hardware: Raspberry Pi 4 (8GB), ESP32, RPLidar A1, BNO-055 IMU, MD13S Motor Drivers.

Navigation: SLAM Toolbox, Nav2, AMCL, TF2 Transforms.
