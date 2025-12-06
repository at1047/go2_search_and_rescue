import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster, StaticTransformBroadcaster
from geometry_msgs.msg import TransformStamped
import math

def euler_to_quaternion(roll, pitch, yaw):
    """
    Convert Euler angles to quaternion.
    """
    qx = math.sin(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) \
        - math.cos(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
    qy = math.cos(roll/2) * math.sin(pitch/2) * math.cos(yaw/2) \
        + math.sin(roll/2) * math.cos(pitch/2) * math.sin(yaw/2)
    qz = math.cos(roll/2) * math.cos(pitch/2) * math.sin(yaw/2) \
        - math.sin(roll/2) * math.sin(pitch/2) * math.cos(yaw/2)
    qw = math.cos(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) \
        + math.sin(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
    return qx, qy, qz, qw


class OdomTFPublisher(Node):
    def __init__(self):
        super().__init__('odom_tf_publisher')

        # STATIC TRANSFORM: base_link → utlidar_lidar
        self.static_br = StaticTransformBroadcaster(self)
        static_t = TransformStamped()
        static_t.header.stamp = rclpy.time.Time().to_msg()
        static_t.header.frame_id = "base_link"
        static_t.child_frame_id = "utlidar_lidar"

        # TODO: fill these in with REAL measured values
        static_t.transform.translation.x = 0.10
        static_t.transform.translation.y = 0.00
        static_t.transform.translation.z = 0.15

        # lidar tilt example (replace)
        roll = 0.0
        pitch = math.radians(-20)
        yaw = 0.0

        qx, qy, qz, qw = euler_to_quaternion(roll, pitch, yaw)
        static_t.transform.rotation.x = qx
        static_t.transform.rotation.y = qy
        static_t.transform.rotation.z = qz
        static_t.transform.rotation.w = qw

        self.static_br.sendTransform(static_t)

        # DYNAMIC TF: odom → base_link
        self.br = TransformBroadcaster(self)
        self.sub = self.create_subscription(
            Odometry,
            '/utlidar/robot_odom',
            self.odom_callback,
            10
        )

    def odom_callback(self, msg):
        t = TransformStamped()
        t.header.stamp = msg.header.stamp
        t.header.frame_id = msg.header.frame_id     # usually "odom"
        t.child_frame_id = msg.child_frame_id       # usually "base_link"

        # copy translation
        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z

        # copy FULL quaternion
        t.transform.rotation = msg.pose.pose.orientation

        self.br.sendTransform(t)


def main():
    rclpy.init()
    rclpy.spin(OdomTFPublisher())
    rclpy.shutdown()


if __name__ == '__main__':
    main()



