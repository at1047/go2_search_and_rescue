#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

import numpy as np
from math import floor, exp

from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import Pose
from tf2_ros import Buffer, TransformListener


class LogOddsMapper(Node):
    def __init__(self):
        super().__init__("log_odds_mapper")

        # Map parameters
        self.declare_parameter("resolution", 0.05)
        self.declare_parameter("width", 500)
        self.declare_parameter("height", 500)
        self.res = self.get_parameter("resolution").value
        self.w   = self.get_parameter("width").value
        self.h   = self.get_parameter("height").value

        # Lidar Z filter
        self.declare_parameter("z_min", 0.1)
        self.declare_parameter("z_max",  0.5)
        self.z_min = self.get_parameter("z_min").value
        self.z_max = self.get_parameter("z_max").value

        # Log-odds params
        self.L_occ  = np.log(0.7 / (1 - 0.7))    # hit
        self.L_free = np.log(0.45 / (1 - 0.45))    # miss
        #self.L_free = np.log(0.1 / (1 - 0.1)) #0.2 I have made undoing obstacles easier 
        self.L_min  = -2.0
        self.L_max  =  3.5

        # Map storage (log odds)
        self.map = np.zeros((self.h, self.w), dtype=np.float32)

        # Center map at (0,0)
        self.origin_x = -self.w * self.res / 2.0
        self.origin_y = -self.h * self.res / 2.0

        # ROS I/O
        self.pc_sub = self.create_subscription(PointCloud2, "/utlidar/cloud_deskewed", self.pc_callback, 10)
        self.map_pub = self.create_publisher(OccupancyGrid, "map", 5)

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)


        self.get_logger().info("Log-odds occupancy mapper initialized")


    def world_to_grid(self, x, y):
        gx = int((x - self.origin_x) / self.res)
        gy = int((y - self.origin_y) / self.res)
        return gx, gy


    def bresenham(self, x0, y0, x1, y1):
        """Return grid cells along the line from (x0,y0) to (x1,y1)."""
        cells = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = -1 if x0 > x1 else 1
        sy = -1 if y0 > y1 else 1
        if dx > dy:
            err = dx / 2.0
            while x != x1:
                cells.append((x, y))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                cells.append((x, y))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        return cells


    def update_log_odds(self, gx, gy, value):
        if 0 <= gx < self.w and 0 <= gy < self.h:
            self.map[gy, gx] = np.clip(self.map[gy, gx] + value, self.L_min, self.L_max)


    def pc_callback(self, msg):

        # Sensor origin is (0,0) in incoming frame
        #ox, oy = self.world_to_grid(0.0, 0.0)
        # Get transform: odom -> utlidar_lidar
        try:
            tf = self.tf_buffer.lookup_transform(
                "odom", "utlidar_lidar", rclpy.time.Time())
        except Exception as e:
            self.get_logger().warn(f"TF lookup failed: {e}")
            return

        # Extract translation
        lx = tf.transform.translation.x
        ly = tf.transform.translation.y

        # Convert to grid coordinates
        ox, oy = self.world_to_grid(lx, ly)

        # Process points
        for x, y, z in point_cloud2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True):
            if not (self.z_min <= z <= self.z_max):
                continue

            gx, gy = self.world_to_grid(x, y)

            # Free space updates (raytrace)
            for fx, fy in self.bresenham(ox, oy, gx, gy):
                self.update_log_odds(fx, fy, self.L_free)

            # Occupied update
            self.update_log_odds(gx, gy, self.L_occ)

        #self.publish_map(msg.header.frame_id)
        self.publish_map("map")


    def publish_map(self, frame_id):
        grid = OccupancyGrid()
        grid.header.stamp = self.get_clock().now().to_msg()
        #grid.header.frame_id = frame_id
        grid.header.frame_id = "map"


        grid.info.resolution = self.res
        grid.info.width  = self.w
        grid.info.height = self.h

        grid.info.origin.position.x = self.origin_x
        grid.info.origin.position.y = self.origin_y
        grid.info.origin.orientation.w = 1.0

        # Convert to 0–100 occupancy values
        p = 1.0 / (1.0 + np.exp(-self.map))
        #grid.data = (p * 100).astype(np.int8).flatten().tolist()
        #NEW CODE STARTS HERE
        binary = np.full_like(self.map, -1, dtype=np.int8)  # default unknown

        p = 1.0 / (1.0 + np.exp(-self.map))

        binary[p > 0.65] = 100   # obstacle
        binary[p < 0.30] = 0     # free

        grid.data = binary.flatten().tolist()
        # NEW CODE ENDS HERE
 

        self.map_pub.publish(grid)



def main(args=None):
    rclpy.init(args=args)
    node = LogOddsMapper()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

