#!/usr/bin/env python3
import sys
import rclpy
from rclpy.node import Node
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QProgressBar, 
                             QComboBox, QGroupBox, QSlider, QFileDialog, QScrollArea)
from PyQt5.QtCore import Qt
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import BatteryState
from std_srvs.srv import Empty
from nav2_simple_commander.robot_navigator import BasicNavigator

class DeliveroApp(QWidget):
    def __init__(self, ros_node):
        super().__init__()
        self.ros_node = ros_node
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("DELIVERO MISSION CONTROL")
        self.setStyleSheet("background-color: #1a1e2a; color: white;")
        
        self.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.setMinimumSize(800, 480) 
        self.showMaximized()
        
        # Main Layout with padding to prevent edge overlap
        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(15, 15, 15, 15)
        outer_layout.setSpacing(20)

        # --- LEFT SIDE: MAP & ENVIRONMENT ---
        left_side = QVBoxLayout()
        left_side.setSpacing(15)
        
        self.map_area = QFrame()
        self.map_area.setStyleSheet("background-color: #0d1117; border: 2px solid #3c424f; border-radius: 5px;")
        self.map_area.setMinimumSize(400, 300)
        
        left_side.addWidget(QLabel("Map Area (View in RViz)"))
        left_side.addWidget(self.map_area)

        # Speed Control Group
        speed_group = QGroupBox("Speed Control")
        speed_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #3c424f; margin-top: 10px; padding-top: 15px; }")
        speed_layout = QVBoxLayout()
        speed_layout.setContentsMargins(10, 15, 10, 10)
        
        self.speed_label = QLabel("Max Speed: 0.20 m/s")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(5)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(20)
        self.speed_slider.valueChanged.connect(self.update_speed_label)
        
        speed_layout.addWidget(self.speed_label)
        speed_layout.addWidget(self.speed_slider)
        speed_group.setLayout(speed_layout)
        left_side.addWidget(speed_group)

        # Environment & Localization
        env_group = QGroupBox("Environment & Localization")
        env_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #3c424f; margin-top: 10px; padding-top: 15px; }")
        env_layout = QVBoxLayout()
        env_layout.setContentsMargins(10, 15, 10, 10)
        env_layout.setSpacing(10)

        map_select_layout = QHBoxLayout()
        self.map_selector = QComboBox()
        self.map_selector.addItems(["map_home2.yaml", "lab_floor.yaml", "office_main.yaml"])
        self.map_selector.setStyleSheet("background-color: #2b303b; padding: 5px; min-height: 30px;")
        
        browse_map_btn = QPushButton("BROWSE")
        browse_map_btn.setStyleSheet("background-color: #4caf50; font-weight: bold; min-height: 35px;")
        browse_map_btn.clicked.connect(self.browse_map_file)
        
        load_map_btn = QPushButton("LOAD MAP")
        load_map_btn.setStyleSheet("background-color: #1976d2; font-weight: bold; min-height: 35px;")
        load_map_btn.clicked.connect(self.change_map_trigger)
        
        map_select_layout.addWidget(self.map_selector)
        map_select_layout.addWidget(browse_map_btn)
        map_select_layout.addWidget(load_map_btn)
        
        self.reloc_btn = QPushButton("🔄 RELOCALIZE (GLOBAL)")
        self.reloc_btn.setStyleSheet("background-color: #455a64; font-weight: bold; padding: 10px; min-height: 40px;")
        self.reloc_btn.clicked.connect(self.ros_node.reinitialize_amcl)

        env_layout.addLayout(map_select_layout)
        env_layout.addWidget(self.reloc_btn)
        env_group.setLayout(env_layout)
        left_side.addWidget(env_group)

        # --- RIGHT SIDE: MISSION CONTROLS (Scrollable) ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none; background-color: transparent;")
        
        right_widget = QWidget()
        right_side = QVBoxLayout(right_widget)
        right_side.setContentsMargins(10, 0, 10, 0)
        right_side.setSpacing(20) # Increased spacing between blocks

        # Battery Status
        bat_group = QGroupBox("Robot Status")
        bat_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #3c424f; padding-top: 15px; }")
        bat_layout = QVBoxLayout()
        bat_layout.setContentsMargins(10, 15, 10, 10)
        self.bat_bar = QProgressBar()
        self.bat_bar.setStyleSheet("QProgressBar { border: 1px solid grey; border-radius: 5px; text-align: center; } QProgressBar::chunk { background-color: #2e7d32; }")
        self.bat_bar.setFixedHeight(25)
        bat_layout.addWidget(QLabel("Battery:"))
        bat_layout.addWidget(self.bat_bar)
        bat_group.setLayout(bat_layout)
        right_side.addWidget(bat_group)

        # Waypoint Navigation
        wp_group = QGroupBox("Waypoints")
        wp_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #3c424f; padding-top: 15px; }")
        wp_layout = QVBoxLayout()
        wp_layout.setContentsMargins(10, 15, 10, 10)
        wp_layout.setSpacing(15)

        grid = QVBoxLayout()
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        self.c1 = QPushButton("C1"); self.c1.setStyleSheet("min-height: 50px; font-weight: bold; background-color: #3c424f;"); self.c1.clicked.connect(lambda: self.ros_node.go_to_waypoint("C1"))
        self.c2 = QPushButton("C2"); self.c2.setStyleSheet("min-height: 50px; font-weight: bold; background-color: #3c424f;"); self.c2.clicked.connect(lambda: self.ros_node.go_to_waypoint("C2"))
        row1.addWidget(self.c1); row1.addWidget(self.c2)
        
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        self.c3 = QPushButton("C3"); self.c3.setStyleSheet("min-height: 50px; font-weight: bold; background-color: #3c424f;"); self.c3.clicked.connect(lambda: self.ros_node.go_to_waypoint("C3"))
        self.c4 = QPushButton("C4"); self.c4.setStyleSheet("min-height: 50px; font-weight: bold; background-color: #3c424f;"); self.c4.clicked.connect(lambda: self.ros_node.go_to_waypoint("C4"))
        row2.addWidget(self.c3); row2.addWidget(self.c4)
        
        grid.addLayout(row1)
        grid.addLayout(row2)
        wp_group.setLayout(grid)
        right_side.addWidget(wp_group)

        # Home Button
        home_btn = QPushButton("GO TO HOME (0)")
        home_btn.setMinimumHeight(70) 
        home_btn.setStyleSheet("background-color: #1976d2; font-weight: bold; font-size: 16px; border-radius: 10px;")
        home_btn.clicked.connect(lambda: self.ros_node.go_to_waypoint("0"))
        right_side.addWidget(home_btn)
        
        right_side.addStretch() 

        scroll_area.setWidget(right_widget)

        # Assemble main layouts
        outer_layout.addLayout(left_side, stretch=2)
        outer_layout.addWidget(scroll_area, stretch=1)
        
        self.setLayout(outer_layout)

    def browse_map_file(self):
        file_filter = "YAML files (*.yaml)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Map", "", file_filter)
        if file_path:
            self.map_selector.addItem(file_path)
            self.map_selector.setCurrentText(file_path)

    def update_speed_label(self, value):
        speed = value / 100.0
        self.speed_label.setText(f"Max Speed: {speed:.2f} m/s")
        self.ros_node.set_speed(speed)

    def change_map_trigger(self):
        selected = self.map_selector.currentText()
        self.ros_node.get_logger().info(f"Map change requested: {selected}")

class DeliveroNode(Node):
    def __init__(self):
        super().__init__('delivero_gui_node')
        self.navigator = BasicNavigator()

        self.waypoints = {
            "0":  {"x": 2.28, "y": -0.237, "w": 1.0},
            "C1": {"x": 3.39, "y": -0.484, "w": 1.0},
            "C2": {"x": 5.12, "y": -0.512, "w": 1.0},
            "C3": {"x": 6.22, "y": -0.559, "w": 1.0},
            "C4": {"x": 1.5,  "y": 0.5,    "w": 1.0}
        }

        self.reloc_client = self.create_client(Empty, '/reinitialize_global_localization')
        self.create_subscription(BatteryState, '/battery_status', self.battery_cb, 10)
        
        self.app = QApplication(sys.argv)
        self.gui = DeliveroApp(self)

    def battery_cb(self, msg):
        self.gui.bat_bar.setValue(int(msg.percentage * 100))

    def set_speed(self, speed):
        self.navigator.setMaxSpeed(speed)

    def reinitialize_amcl(self):
        if self.reloc_client.service_is_ready():
            self.reloc_client.call_async(Empty.Request())

    def go_to_waypoint(self, name):
        if name in self.waypoints:
            wp = self.waypoints[name]
            goal = PoseStamped()
            goal.header.frame_id = 'map'
            goal.header.stamp = self.get_clock().now().to_msg()
            goal.pose.position.x = wp["x"]
            goal.pose.position.y = wp["y"]
            goal.pose.orientation.w = wp["w"]
            self.navigator.goToPose(goal)

def main():
    rclpy.init()
    node = DeliveroNode()
    while rclpy.ok():
        node.app.processEvents()
        rclpy.spin_once(node, timeout_sec=0.1)
    rclpy.shutdown()

if __name__ == '__main__':
    main()