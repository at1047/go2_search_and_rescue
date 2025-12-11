from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_share = get_package_share_directory('go2_sar_pkg')
    params_file = os.path.join(pkg_share, "config", "utlidar_slam.yaml")

    return LaunchDescription([
        Node(
            package='slam_toolbox',
            executable='sync_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[params_file],
            remappings = [("/scan","/utlidar/scan")]
        )
    ])

