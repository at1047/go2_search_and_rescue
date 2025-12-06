import rclpy
from rclpy.node import Node
from builtin_interfaces.msg import Time
import subprocess

class ClockSync(Node):
    def __init__(self):
        super().__init__('clock_sync')
        self.sub = self.create_subscription(Time, '/robot_time', self.cb, 10)

    def cb(self, msg):
        secs = msg.sec
        nsecs = msg.nanosec
        timestamp = secs + nsecs * 1e-9

        cmd = ["sudo", "date", "-s", f"@{timestamp: .6f}"]
        subprocess.Popen(cmd)

def main ():
    rclpy.init()
    node = ClockSync()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__="__main__":
    main()
