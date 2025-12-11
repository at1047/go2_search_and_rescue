from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from pathlib import Path

def generate_launch_description():

    # Path to NAV2 navigation_launch.py
    nav2_launch_file = Path(
        "/opt/ros/foxy/share/nav2_bringup/launch/navigation_launch.py"
    )

    # Path to your params file
    nav2_params = "/home/unitree/go2_search_and_rescue/src/go2_sar_pkg/config/nav2_params2.yaml"

    # Include NAV2 properly
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(nav2_launch_file)),
        launch_arguments={
            'params_file': nav2_params,
            'use_sim_time': 'false'
        }.items()
    )

    return LaunchDescription([

        # 1) Static TF: base_link → utlidar_lidar
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='lidar_static_tf',
            arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'utlidar_lidar']
        ),

        # 2) PointCloud → OccupancyGrid
        Node(
            package='go2_sar_pkg',
            executable='pc_to_og',
            name='pc_to_og'
        ),

        # 3) odom → base_link TF broadcaster
        Node(
            package='go2_sar_pkg',
            executable='odom_tf_broadcaster',
            name='odom_tf_broadcaster'
        ),

        # 4) map → odom static TF publisher
        Node(
            package='go2_sar_pkg',
            executable='map_to_odom_static',
            name='map_to_odom_static'
        ),

        # 5) NAV2 Bringup
        nav2_launch,

        # 6) Explorer node
        Node(
            package='custom_explorer',
            executable='explorer',
            name='explorer',
            remappings=[('/map', '/map')]
        ),

        # # 7) Frontier visualization
        # Node(
        #     package='custom_explorer',
        #     executable='frontier_viz',
        #     name='frontier_viz'
        # ),

        # 8) Translate goal from odom to utlidar
        Node(
            package='custom_explorer',
            executable='direction_to_goal',
            name='direction_to_goal'
            ),
        # 9) RViz2 with custom config
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', '/home/unitree/go2_search_and_rescue/src/go2_sar_pkg/rviz2/go2_nav_config.rviz'],
            output='screen'
            )
        ])

