#! /usr/bin/env python
# -*- coding: utf-8 -*-

import rclpy
import math
from rclpy.exceptions import ROSInterruptException
from rclpy.node import Node
import rclpy.logging

from std_msgs.msg import Int16MultiArray
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


class ControllerNode(Node):

    def __init__(self):
        super().__init__("mecanum_drive_controller")
        self.node_name = self.get_name()

        self.get_node_parameter()

        self.get_logger().info("{0} started".format(self.node_name))

        self.last_twist_time = self.get_clock().now()

    def get_node_parameter(self):
        self.parameters = {
            "wheel_base_width": 1,
            "wheel_base_length": 1,
            "wheel_radius": 1,
            "invert_right": True,
            "rate": 100,
        }

        for key in self.parameters.keys():
            self.declare_parameter(key, self.parameters[key])
            self.parameters[key] = self.get_parameter(key).value
            self.get_logger().info(
                f"Publish ros2 parameter, {key}: {self.parameters[key]}")

    def createInterfaces(self):
        self.odometyuPub = self.create_publisher(
            Odometry, "kinematics/odometry", 10)


def main(args=None):
    rclpy.init(args=args)
    node = ControllerNode()
    try:
        rclpy.spin(node)
    except ROSInterruptException:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown(node)


if __name__ == '__main__':
    main()
