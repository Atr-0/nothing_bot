#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rclpy
from rclpy.node import Node
import rclpy.qos
from geometry_msgs.msg import Twist
import time
from utils import getRobotPos, distance


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

        try:
            # while (distance({oldPos[0],oldPos[1]},{pos[0],pos[1]})<(dis-0.1)):
            while (dis >= 0):
                twist = Twist()
                twist.linear.x = x*speed
                twist.linear.y = y*speed
                twist.linear.z = z*speed
                twist.angular.x = 0.0
                twist.angular.y = 0.0
                twist.angular.z = th*turn
                self.pub.publish(twist)
                time.sleep(1)
                # pos=getRobotPos()
                dis = dis-1
        except IndexError and TypeError and ValueError as e:
            print(f'error')
            print(e)

        finally:
            twist = Twist()
            twist.linear.x = 0.0
            twist.linear.y = 0.0
            twist.linear.z = 0.0
            twist.angular.x = 0.0
            twist.angular.y = 0.0
            twist.angular.z = 0.0
            self.pub.publish(twist)

            rclpy.shutdown(Node)
