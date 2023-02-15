#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rclpy
from rclpy.node import Node
import rclpy.qos
from geometry_msgs.msg import Twist
from std_msgs.msg import Int32
from rclpy.exceptions import ROSInterruptException
import time
import numpy as np
'''
 [0,0,0,0]         [0,0,0,0,0,0]
 [0,0,0,0]         [0,0,0,0,0,0]
 [0,0,0,0]------>  [0,0,0,0,0,0]
 [0,0,0,0]         [0,0,0,0,0,0]
 [0,0,0,0]
 [0,0,0,0]
'''
sensor_matrix = np.zeros([6, 4])


class basicMove(Node):
    def __init__(self, vel, turnVel, dis):
        rclpy.init(args=None)
        super().__init__("basicMove")

        self.pub = self.create_publisher(
            Twist, 'cmd_vel', 10)
        self.speed = vel
        self.turn = turnVel
        self.x = 1.0
        self.y = 0.0
        self.z = 0.0
        self.th = 1.0
        self.create_rate(40)
        self.twist = Twist()

        self.line_sensor = self.create_subscription(
            'line_sensor', Int32, self.line_sensor_callback())

        while (dis >= 0):
            time.sleep(0.02)
            dis = dis-1

    def line_sensor_callback(self, data):
        temp = data.data
        mijishu = 19
        temp = 1024*1024-temp-1
        global sv
        for i in range(1, 7):
            for j in range(1, 5):
                sensor_matrix[i-1][4-j] = temp//2**mijishu
                temp = temp % 2**mijishu
                mijishu = mijishu-1
            pass
        pass

    def publish_twist(self):
        self.pub.publish(self.twist)

        self.twist.linear.x = self.x*self.speed
        self.twist.linear.y = self.y*self.speed
        self.twist.linear.z = self.z*self.speed
        self.twist.angular.x = 0.0
        self.twist.angular.y = 0.0
        self.twist.angular.z = self.th*self.turn


def main(args=None):
    rclpy.init(args=args)
    node = basicMove()
    try:
        rclpy.spin(node)
    except ROSInterruptException:
        pass
    finally:
        node.pub.publish(node.twist)

        node.twist.linear.x = 0.0
        node.twist.linear.y = 0.0
        node.twist.linear.z = 0.0
        node.twist.angular.x = 0.0
        node.twist.angular.y = 0.0
        node.twist.angular.z = 0.0

        node.pub.publish(node.twist)
        node.destroy_rate()
        node.destroy_node()
        rclpy.shutdown(node)


if __name__ == "__main__":
    main()
