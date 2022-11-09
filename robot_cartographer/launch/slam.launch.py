import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch import actions
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():

    pkg_dir = get_package_share_directory('robot_description')
    rviz_config_file= os.path.join(get_package_share_directory('robot_cartographer'), 'rviz2', 'carto_slam.rviz')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_dir, "launch",'gazebo.launch.py')
        ),
    )

    lua_configuration_directory = os.path.join(
        get_package_share_directory('robot_cartographer'), 'config')
    lua_configuration_name = 'lidar_2d.lua'

    cartographer = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        arguments=['-configuration_directory', lua_configuration_directory,
                   '-configuration_basename', lua_configuration_name ],
        remappings = [('scan', 'scan')],
        output='screen',
    )

    cartographer_map = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        name='cartographer_occupancy_grid_node',
        arguments=['-resolution', '0.05'],
        output='screen',
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        output='screen',
    )

    return LaunchDescription([

        gazebo,
        cartographer,
        cartographer_map,
        rviz
    ])