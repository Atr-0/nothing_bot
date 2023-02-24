#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rclpy
from rclpy.node import Node
import rclpy.qos
from geometry_msgs.msg import Vector3
from std_msgs.msg import String
import time


class motor_control(Node):
    def __init__(self, a, b):
        rclpy.init(args=None)
        super().__init__("motor_control")
        self.pub = self.create_publisher(
            String, 'action_msg', 10)
        temp = a+"1"+b+"%s"
        hello_str = temp
        self.pub.publish(hello_str)
        time.sleep(0.5)

        self.destroy_node()
        rclpy.shutdown()
