/*
*  3iRoboticsLIDAR System II
*  Driver Interface
*
*  Copyright 2017 3iRobotics
*  All rights reserved.
*
*	Author: 3iRobotics, Data:2017-09-15
*
*/

#include <rclcpp/rclcpp.hpp>
#include "sensor_msgs/msg/laser_scan.hpp"

#define RAD2DEG(x) ((x)*180./M_PI)

void scanCallback(const sensor_msgs::msg::LaserScan::ConstPtr& scan)
{
    int count = scan->scan_time / scan->time_increment;
//    ROS_INFO("I heard a laser scan %s[%d]:", scan->header.frame_id.c_str(), count);
//    ROS_INFO("angle_range, %f, %f", RAD2DEG(scan->angle_min), RAD2DEG(scan->angle_max));
  
    for(int i = 0; i < count; i++) {
        float degree = RAD2DEG(scan->angle_min + scan->angle_increment * i);
//        ROS_INFO(": [%f, %f]", degree, scan->ranges[i]);
    }
}

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<rclcpp::Node>("delta_2b_lidar_node_client");
    
    // std::shared_ptr<rclcpp::Node> nh;
    rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr sub = node->create_subscription<sensor_msgs::msg::LaserScan>("/scan", 1000, scanCallback);
    rclcpp::spin(node);
    // rclcpp::shutdown();

    return 0;
}