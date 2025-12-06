import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster, StaticTransformBroadcaster
from geometry_msgs.msg import TransformStamped


class OdomTFPublisher(Node):
    def __init__(self):
        super().__init__('odom_tf_publisher')

        # dynamic broadcaster
        self.br = TransformBroadcaster(self)

        # static broadcaster for the lidar
        self.static_br1 = StaticTransformBroadcaster(self)
        self.static_br2 = StaticTransformBroadcaster(self)

        self.publish_static_lidar_tf(self.static_br1)
        self.odom_callback(self.static_br2)


    def odom_callback(self, static_br):
        # odom -> base_link TF from odometry
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = "odom"            # usually "odom"
        t.child_frame_id = "base_link"              # usually "base_link"

        t.transform.translation.x = 0.0
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.0
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0

        static_br.sendTransform(t)

    def publish_static_lidar_tf(self, static_br):
        # base_link -> utlidar_lidar
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = "base_link"
        t.child_frame_id = "utlidar_lidar"

        t.transform.translation.x = 0.0
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.0
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0

        # publish once (static)
        static_br.sendTransform(t)


def main():
    rclpy.init()
    rclpy.spin(OdomTFPublisher())
    rclpy.shutdown()


if __name__ == '__main__':
    main()

