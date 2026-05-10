import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
import serial
import math

class ESP32Bridge(Node):
    def __init__(self):
        super().__init__('esp32_bridge')
        
        # --- Robot Physical Constants (ADJUST THESE) ---
        self.wheel_radius = 0.033       # meters
        self.wheel_separation = 0.17    # meters
        self.ticks_per_rev = 1440       # Adjust to your encoder

        # --- Noise filter threshold ---
        self.VELOCITY_THRESHOLD = 0.005  # m/s — below this, treat as zero
        
        try:
            self.ser = serial.Serial('/dev/ttyUSB1', 115200, timeout=0.1)
            self.get_logger().info("ESP32 Serial Bridge Started")
        except Exception as e:
            self.get_logger().error(f"Serial Error: {e}")

        self.subscription = self.create_subscription(Twist, '/cmd_vel', self.cmd_callback, 10)
        self.odom_pub = self.create_publisher(Odometry, '/odom_wheels', 10)
        self.timer = self.create_timer(0.05, self.read_serial)

    def cmd_callback(self, msg):
        linear = msg.linear.x * 255.0
        angular = msg.angular.z * 150.0
        m1, m2 = int(-linear + angular), int(-linear - angular)
        command = f"v {max(min(m1, 255), -255)} {max(min(m2, 255), -255)}\n"
        self.ser.write(command.encode('utf-8'))

    def read_serial(self):
        if self.ser.in_waiting > 0:
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith("e"):
                try:
                    parts = line.split()
                    left_ticks_s  = float(parts[1])
                    right_ticks_s = float(parts[2])

                    # Convert ticks/s to m/s
                    v_left  = (left_ticks_s  / self.ticks_per_rev) * (2 * math.pi * self.wheel_radius)
                    v_right = (right_ticks_s / self.ticks_per_rev) * (2 * math.pi * self.wheel_radius)

                    # Calculate linear and angular velocity
                    v_linear  = (v_right + v_left) / 2.0
                    v_angular = (v_right - v_left) / self.wheel_separation

                    # ✅ Zero out encoder noise when robot is stationary
                    if abs(v_linear) < self.VELOCITY_THRESHOLD:
                        v_linear = 0.0
                    if abs(v_angular) < self.VELOCITY_THRESHOLD:
                        v_angular = 0.0

                    # Publish Odometry message
                    odom = Odometry()
                    odom.header.stamp = self.get_clock().now().to_msg()
                    odom.header.frame_id = "odom"
                    odom.child_frame_id = "base_link"
                    odom.twist.twist.linear.x  = v_linear
                    odom.twist.twist.angular.z = v_angular

                    # Covariance — tells EKF how much to trust this data
                    odom.twist.covariance[0]  = 0.001   # linear x
                    odom.twist.covariance[35] = 0.001   # angular z

                    self.odom_pub.publish(odom)
                except:
                    pass

def main(args=None):
    rclpy.init(args=args)
    node = ESP32Bridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if hasattr(node, 'ser'):
            node.ser.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()