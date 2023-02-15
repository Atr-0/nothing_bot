# Copyright (c) 2021 Juan Miguel Jimeno
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition


def generate_launch_description():
    laser_sensor_name = os.getenv('LINOROBOT2_LASER_SENSOR', '')
    base_laser_sensor_name = os.getenv('LINOROBOT2_BASE_LASER_SENSOR', '')
    sensors_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_bringup'), 'launch', 'sensors.launch.py']
    )
    realsense_launch_path = PathJoinSubstitution(
        [FindPackageShare('realsense2_camera'), 'launch', 'rs_launch.py']
    )

    joy_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_bringup'), 'launch',
         'joy_teleop.launch.py']
    )

    description_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_description'),
         'launch', 'description.launch.py']
    )
    location_launch_path = PathJoinSubstitution(
        [FindPackageShare('robot_cartographer'), 'launch',
         'demo_backpack_2d_localization.launch.py']
    )
    navigation_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_navigation'),
         'launch', 'navigation.launch.py']
    )

    ekf_config_path = PathJoinSubstitution(
        [FindPackageShare("linorobot2_base"), "config", "ekf.yaml"]
    )

    laser_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_bringup'), 'launch', 'lasers.launch.py']
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            name='base_serial_port',
            default_value='/dev/linorobot',
            # default_value='/dev/ttyACM0',
            description='Linorobot Base Serial Port'
        ),

        DeclareLaunchArgument(
            name='joy',
            default_value='true',
            description='Use Joystick'
        ),

        Node(
            package='micro_ros_agent',
            executable='micro_ros_agent',
            name='micro_ros_agent',
            output='screen',
            arguments=['serial', '--dev',
                       LaunchConfiguration("base_serial_port")]
        ),

        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[
                ekf_config_path
            ],
            # remappings=[("/imu/data", "/imu/data_robot")]
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(description_launch_path)
        ),

        # IncludeLaunchDescription(
        #     PythonLaunchDescriptionSource(realsense_launch_path)
        # ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(sensors_launch_path),
        ),

        # IncludeLaunchDescription(
        #     PythonLaunchDescriptionSource(navigation_launch_path),
        # ),

        # IncludeLaunchDescription(
        #     PythonLaunchDescriptionSource(joy_launch_path),
        #     condition=IfCondition(LaunchConfiguration("joy")),
        # ),

        # IncludeLaunchDescription(
        #     PythonLaunchDescriptionSource(location_launch_path),
        # ),
        # Node(
        #     package="tf2_ros",
        #     executable="static_transform_publisher",
        #     output="screen",
        #     arguments=[("0", "0", "0", "0", "0", "0", "map", "odom")]
        # ),
        # Node(
        #     package="tf2_ros",
        #     executable="static_transform_publisher",
        #     output="screen",
        #     arguments=[("0", "0", "0", "0", "0", "0", "map", "laser")]
        # ),
        # Node(
        #     package="tf2_ros",
        #     executable="static_transform_publisher",
        #     output="screen",
        #     arguments=["0", "0", "0", "0", "0", "0",
        #                "camera_link", "base_footprint"]
        # ),

    ])
