import os
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    package_name = 'lidar'
    
    ld = LaunchDescription()
    serial_port = LaunchConfiguration('serial_port', default='/dev/ttyUSB0')
    frame_id = LaunchConfiguration('frame_id', default='laser')

    delta_lidar = Node(
        package='lidar',
        executable='delta_lidar_node',
        output='screen',
        parameters=[{'serial_port':serial_port},{'frame_id':frame_id}]
        )

    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time':False}]
        )

    ld.add_action(delta_lidar)
    # ld.add_action(rviz2_node)

    return ld
