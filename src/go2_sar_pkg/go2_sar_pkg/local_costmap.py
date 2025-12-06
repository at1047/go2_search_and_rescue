import math
import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import PointStamped
import time

import tf2_ros
from tf2_ros import LookupException, ConnectivityException, ExtrapolationException


class DynamicLocalCostmap(Node):
    def __init__(self):
        super().__init__("dynamic_local_costmap")

        # PARAMETERS
        self.declare_parameter("scan_topic", "/utlidar/scan")
        self.declare_parameter("global_frame", "map")
        self.declare_parameter("robot_base_frame", "base_link")

        self.declare_parameter("resolution", 0.05)
        self.declare_parameter("width", 8.0)
        self.declare_parameter("height", 8.0)

        self.declare_parameter("obstacle_range", 6.0)
        self.declare_parameter("raytrace_range", 7.0)

        self.declare_parameter("rolling_window", True)

        # Load parameters
        self.scan_topic = self.get_parameter("scan_topic").value
        self.global_frame = self.get_parameter("global_frame").value
        self.robot_frame = self.get_parameter("robot_base_frame").value

        self.resolution = float(self.get_parameter("resolution").value)
        self.width = float(self.get_parameter("width").value)
        self.height = float(self.get_parameter("height").value)

        self.obstacle_range = float(self.get_parameter("obstacle_range").value)
        self.raytrace_range = float(self.get_parameter("raytrace_range").value)
        self.use_rolling = self.get_parameter("rolling_window").value

        # Grid dimensions
        self.map_w = int(self.width / self.resolution)
        self.map_h = int(self.height / self.resolution)

        # TF
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Costmap storage (initialized once TF is available)
        self.costmap = None
        self.center_x = None
        self.center_y = None

        # ROS
        self.scan_sub = self.create_subscription(
            LaserScan, self.scan_topic, self.scan_callback, 10
        )
        self.pub = self.create_publisher(OccupancyGrid, "/local_costmap/costmap", 10)

        # Wait for initial TF to be available
        self.wait_for_initial_tf()

        self.get_logger().info("Dynamic Local Costmap Node (patched, stable) started.")

    # ---------------------------------------------------
    # WAIT FOR FIRST TRANSFORM BEFORE RUNNING ANYTHING
    # ---------------------------------------------------
    def wait_for_initial_tf(self):
        self.get_logger().info("Waiting for TF map -> base_link ...")
        while rclpy.ok():
            try:
                self.tf_buffer.lookup_transform(
                    self.global_frame,
                    self.robot_frame,
                    rclpy.time.Time(),
                    timeout=rclpy.duration.Duration(seconds=0.5)
                )
                self.get_logger().info("TF map->base_link available.")
                return
            except Exception:
                self.get_logger().warn("Still waiting for map->base_link TF...")
                time.sleep(0.1)

    # ---------------------------------------------------
    # Costmap Init / Shift
    # ---------------------------------------------------
    def init_costmap(self, cx, cy, reset=False):
        new_costmap = OccupancyGrid()
        new_costmap.header.frame_id = self.global_frame

        new_costmap.info.resolution = self.resolution
        new_costmap.info.width = self.map_w
        new_costmap.info.height = self.map_h

        ox = cx - self.width / 2.0
        oy = cy - self.height / 2.0

        new_costmap.info.origin.position.x = ox
        new_costmap.info.origin.position.y = oy
        new_costmap.info.origin.orientation.w = 1.0

        # Reset or shift old data
        if reset or self.costmap is None:
            new_costmap.data = [-1] * (self.map_w * self.map_h)
        else:
            new_costmap.data = [-1] * (self.map_w * self.map_h)
            for my in range(self.map_h):
                for mx in range(self.map_w):
                    wx_old = self.costmap.info.origin.position.x + mx * self.resolution
                    wy_old = self.costmap.info.origin.position.y + my * self.resolution

                    mx_new, my_new = self.world_to_map(wx_old, wy_old, new_costmap)
                    if mx_new is not None:
                        new_costmap.data[my_new * self.map_w + mx_new] = \
                            self.costmap.data[my * self.map_w + mx]

        self.costmap = new_costmap
        self.center_x = cx
        self.center_y = cy

    # ---------------------------------------------------
    # Helper Functions
    # ---------------------------------------------------
    def world_to_map(self, wx, wy, costmap=None):
        if costmap is None:
            costmap = self.costmap
        ox = costmap.info.origin.position.x
        oy = costmap.info.origin.position.y

        mx = int((wx - ox) / self.resolution)
        my = int((wy - oy) / self.resolution)

        if 0 <= mx < self.map_w and 0 <= my < self.map_h:
            return mx, my
        return None, None

    def set_cell(self, mx, my, val):
        self.costmap.data[my * self.map_w + mx] = val

    # ---------------------------------------------------
    # Raytracing Free Space
    # ---------------------------------------------------
    def raytrace(self, x0, y0, x1, y1):
        mx0, my0 = self.world_to_map(x0, y0)
        mx1, my1 = self.world_to_map(x1, y1)

        if mx0 is None or mx1 is None:
            return

        dx = abs(mx1 - mx0)
        dy = abs(my1 - my0)
        x, y = mx0, my0
        sx = 1 if mx1 >= mx0 else -1
        sy = 1 if my1 >= my0 else -1

        if dx >= dy:
            err = dx / 2
            while x != mx1:
                self.set_cell(x, y, 0)  # free
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2
            while y != my1:
                self.set_cell(x, y, 0)
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy

    # ---------------------------------------------------
    # Main LiDAR Callback
    # ---------------------------------------------------
    def scan_callback(self, scan):
        # Attempt TF lookup with tolerance
        try:
            tf = self.tf_buffer.lookup_transform(
                self.global_frame,
                self.robot_frame,
                rclpy.time.Time(),
                timeout=rclpy.duration.Duration(seconds=0.05)
            )
        except Exception:
            self.get_logger().warn("TF lookup failed this scan — skipping.")
            return

        rx = tf.transform.translation.x
        ry = tf.transform.translation.y

        # Initialize costmap or shift rolling window
        if self.costmap is None:
            self.init_costmap(rx, ry, reset=True)
        elif self.use_rolling:
            self.init_costmap(rx, ry, reset=False)

        # Process LiDAR beams
        angle = scan.angle_min
        for r in scan.ranges:
            if not math.isfinite(r) or r < 0.05:
                angle += scan.angle_increment
                continue

            r_clear = min(r, self.raytrace_range)

            # Compute hit in lidar frame
            p = PointStamped()
            p.header.frame_id = scan.header.frame_id
            p.point.x = r_clear * math.cos(angle)
            p.point.y = r_clear * math.sin(angle)

            try:
                pg = self.tf_buffer.transform(p, self.global_frame)
            except Exception:
                angle += scan.angle_increment
                continue

            # Raytrace clear
            self.raytrace(rx, ry, pg.point.x, pg.point.y)

            # Mark obstacle endpoint
            if r <= self.obstacle_range:
                mx, my = self.world_to_map(pg.point.x, pg.point.y)
                if mx is not None:
                    self.set_cell(mx, my, 100)

            angle += scan.angle_increment

        # Publish
        self.costmap.header.stamp = self.get_clock().now().to_msg()
        self.pub.publish(self.costmap)


def main(args=None):
    rclpy.init(args=args)
    node = DynamicLocalCostmap()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

