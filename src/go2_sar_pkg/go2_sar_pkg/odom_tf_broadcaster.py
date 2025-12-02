import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped

class OdomTFPublisher(Node):
    def __init__(self):
        super().__init__('odom_tf_publisher')
        self.br = TransformBroadcaster(self)
        self.sub = self.create_subscription(
            Odometry,
           '/utlidar/robot_odom',
            self.callback,
            10)

    def callback(self, msg):
        t = TransformStamped()
        t.header = msg.header
        t.header.stamp = self.get_clock().now().to_msg()
        t.child_frame_id = msg.child_frame_id
        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z
        t.transform.rotation.x = msg.pose.pose.orientation.x
        t.transform.rotation.y = msg.pose.pose.orientation.y
        t.transform.rotation.z = msg.pose.pose.orientation.z
        t.transform.rotation.w = 1.0
        self.br.sendTransform(t)


def main():
    rclpy.init()
    rclpy.spin(OdomTFPublisher())
    rclpy.shutdown()

if __name__ == '__main__':
    main()

