import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid, MapMetaData
from builtin_interfaces.msg import Time

class EmptyMapPublisher(Node):
    def __init__(self):
        super().__init__("empty_map_publisher")

        self.publisher = self.create_publisher(OccupancyGrid, "/map", 10)

        # Publish at 1 Hz so Nav2 always has a fresh map
        self.timer = self.create_timer(1.0, self.publish_map)

        # Build a small, empty map:
        self.map = OccupancyGrid()
        self.map.header.frame_id = "map"

        # Metadata
        width = 200   # 200 cells
        height = 200  # 200 cells
        resolution = 0.05  # 5 cm per cell

        info = MapMetaData()
        info.resolution = resolution
        info.width = width
        info.height = height
        info.origin.position.x = - (width * resolution) / 2.0
        info.origin.position.y = - (height * resolution) / 2.0
        info.origin.position.z = 0.0

        # All free space (-1 = unknown, 0 = free, 100 = occupied)
        self.map.info = info
        self.map.data = [-1] * (width * height)   # unknown map

    def publish_map(self):
        self.map.header.stamp = self.get_clock().now().to_msg()
        self.publisher.publish(self.map)

def main():
    rclpy.init()
    node = EmptyMapPublisher()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()

