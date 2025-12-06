import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid, MapMetaData
import math

class FakeDogMaps(Node):
    def __init__(self):
        super().__init__('fake_dog_maps')

        self.map_pub = self.create_publisher(OccupancyGrid, '/map', 10)
        self.map_meta_pub = self.create_publisher(MapMetaData, '/map_metadata', 10)

        self.local_pub = self.create_publisher(OccupancyGrid, '/local_costmap', 10)
        self.local_meta_pub = self.create_publisher(MapMetaData, '/local_costmap_metadata', 10)

        self.resolution = 0.05
        self.global_w = 200
        self.global_h = 200
        self.local_w = 80
        self.local_h = 80

        self.t = 0.0
        self.robot_x = 5.0
        self.robot_y = 5.0

        self.global_map = self.build_global_map()
        self.publish_global_map()

        self.create_timer(0.2, self.update_local_costmap)

    def build_global_map(self):
        grid = OccupancyGrid()
        grid.header.frame_id = "map"

        grid.info = MapMetaData()
        grid.info.resolution = self.resolution
        grid.info.width = self.global_w
        grid.info.height = self.global_h
        grid.info.origin.position.x = 0.0
        grid.info.origin.position.y = 0.0
        grid.info.origin.orientation.w = 1.0

        data = [0] * (self.global_w * self.global_h)

        # Add some fake obstacles
        for i in range(40, 60):
            for j in range(100, 120):
                data[i * self.global_w + j] = 100

        for i in range(120, 140):
            for j in range(40, 60):
                data[i * self.global_w + j] = 100

        grid.data = data
        return grid

    def publish_global_map(self):
        now = self.get_clock().now().to_msg()
        self.global_map.header.stamp = now
        self.global_map.info.map_load_time = now

        self.map_meta_pub.publish(self.global_map.info)
        self.map_pub.publish(self.global_map)

    def update_local_costmap(self):
        self.t += 0.1
        self.robot_x = 5.0 + math.cos(self.t) * 2.0
        self.robot_y = 5.0 + math.sin(self.t) * 2.0

        grid = OccupancyGrid()
        grid.header.frame_id = "map"
        now = self.get_clock().now().to_msg()
        grid.header.stamp = now

        meta = MapMetaData()
        meta.resolution = self.resolution
        meta.width = self.local_w
        meta.height = self.local_h
        meta.origin.position.x = self.robot_x - (self.local_w*self.resolution)/2
        meta.origin.position.y = self.robot_y - (self.local_h*self.resolution)/2
        meta.origin.orientation.w = 1.0

        grid.info = meta

        data = [0] * (self.local_w * self.local_h)

        cx = int(self.local_w/2 + math.sin(self.t)*10)
        cy = int(self.local_h/2 + math.cos(self.t)*10)
        if 0 <= cx < self.local_w and 0 <= cy < self.local_h:
            data[cy * self.local_w + cx] = 100

        grid.data = data

        self.local_meta_pub.publish(grid.info)
        self.local_pub.publish(grid)


def main(args=None):
    rclpy.init(args=args)
    node = FakeDogMaps()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

