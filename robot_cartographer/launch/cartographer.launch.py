import os
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    # 定位到功能包的地址
    pkg_share = FindPackageShare(package='robot_cartographer').find('robot_cartographer')
    
    #=====================运行节点需要的配置=======================================================================
    # 是否使用仿真时间
    use_sim_time = LaunchConfiguration('use_sim_time', default='False')
    # 地图的分辨率
    resolution = LaunchConfiguration('resolution', default='0.05')
    # 地图的发布周期
    publish_period_sec = LaunchConfiguration('publish_period_sec', default='1.0')
    # 配置文件夹路径
    configuration_directory = LaunchConfiguration('configuration_directory',default= os.path.join(pkg_share, 'config') )
    # 配置文件
    configuration_basename = LaunchConfiguration('configuration_basename', default='backpack_2d.lua')

    
    #=====================声明三个节点，cartographer/occupancy_grid_node/rviz_node=================================
    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=['-configuration_directory', configuration_directory,
                   '-configuration_basename', configuration_basename])

    occupancy_grid_node = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        name='cartographer_occupancy_grid_node',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=['-resolution', resolution, '-publish_period_sec', publish_period_sec],
        remappings = [
            ('echoes', 'scan')],
            )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments = ['-d', pkg_share + '/rviz/carto.rviz'],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen')
    tf_node = Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            output="screen" ,
            arguments=[("0", "0", "0", "0", "0", "0", "map", "odom_frame")]
        )
    # tf_node1 = Node(
    #         package="tf2_ros",
    #         executable="static_transform_publisher",
    #         output="screen" ,
    #         arguments=["0", "0", "0", "0", "0", "0", "camera_link", "base_footprint"]
    #     )

    realsense_launch_path = PathJoinSubstitution(
        [FindPackageShare('realsense2_camera'), 'launch', 'rs_launch.py']
    )

    # serial_port_front = LaunchConfiguration('serial_port', default='/dev/ttyUSB0')
    # frame_idF_front = LaunchConfiguration('frame_id', default='laser')
    # scan_front = LaunchConfiguration('lidar_scan', default='/scan')
    # delta_lidar_front = Node(
    #     package='lidar',
    #     executable='delta_lidar_node',
    #     output='screen',
    #     parameters=[{'serial_port':serial_port_front},{'frame_id':frame_idF_front},{'lidar_scan':scan_front}]
    #     )

    # serial_port_behind= LaunchConfiguration('serial_port', default='/dev/ttyUSB1')
    # frame_id_behind = LaunchConfiguration('frame_id', default='laser')
    # scan_behind = LaunchConfiguration('lidar_scan', default='/scan_2')
    # delta_lidar_behind = Node(
    #     package='lidar',
    #     executable='delta_lidar_node',
    #     output='screen',
    #     parameters=[{'serial_port':serial_port_behind},{'frame_id':frame_id_behind},{'lidar_scan':scan_behind}]
    #     )

    #===============================================定义启动文件========================================================
    ld = LaunchDescription()
    # ld.add_action(delta_lidar_front)
    # ld.add_action(delta_lidar_beh ind)
    ld.add_action(cartographer_node)
    ld.add_action(occupancy_grid_node)
    ld.add_action(rviz_node)   
    # ld.add_action(tf_node1) 
    ld.add_action(tf_node) 
    return ld
