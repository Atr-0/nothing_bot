#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rclpy
from rclpy.node import Node
import rclpy.qos
from geometry_msgs.msg import Twist
from rclpy.exceptions import ROSInterruptException
import time


class basicMove(Node):
    def __init__(self, vel, turnVel, dis):
        rclpy.init(args=None)
        super().__init__("basicMove")

        self.pub = self.create_publisher(
            Twist, 'cmd_vel', 10)
        speed = vel
        turn = turnVel
        x = 1.0
        y = 0.0
        z = 0.0
        th = 1.0
        # pos=getRobotPos()
        # oldPos=pos
        twist = Twist()
        try:
            while (dis >= 0):
                self.pub.publish(twist)
                twist.linear.x = x*speed
                twist.linear.y = y*speed
                twist.linear.z = z*speed
                twist.angular.x = 0.0
                twist.angular.y = 0.0
                twist.angular.z = th*turn
                time.sleep(0.02)

                dis = dis-1
        except ROSInterruptException:
            pass
        finally:
            self.pub.publish(twist)
            twist.linear.x = 0.0
            twist.linear.y = 0.0
            twist.linear.z = 0.0
            twist.angular.x = 0.0
            twist.angular.y = 0.0
            twist.angular.z = 0.0

            self.destroy_node()
            rclpy.shutdown(self)
        self.pub.publish(twist)
