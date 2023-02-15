#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rclpy
from rclpy.node import Node, Subscription
import rclpy.qos
from geometry_msgs.msg import Twist
from std_msgs.msg import Int32
from rclpy.exceptions import ROSInterruptException
import time
import numpy as np
np.set_printoptions(threshold=np.inf)
sensor_matrix = np.zeros([6, 4])


class movement(Node):
    def __init__(self, vel, turnVel, dis):
        rclpy.init(args=None)
        super().__init__("movement")

        self.pub = self.create_publisher(
            Twist, 'cmd_vel', 10)
        self.speed = vel
        self.turn = turnVel
        self.x = 0.0
        self.y = 1.0
        self.z = 0.0
        self.th = 1.0
        self.rate = self.create_rate(500)
        self.twist = Twist()
        node_sub = line_sensor_subscription()

        while dis > 0:
            rclpy.spin_once(node_sub)
            self.publish_twist()
            print(sensor_matrix)
            # self.rate.sleep()
            dis = dis-1
        node_sub.destroy_node()

    def publish_twist(self):
        self.pub.publish(self.twist)
        self.twist.linear.x = self.x*self.speed
        self.twist.linear.y = self.y*self.speed
        self.twist.linear.z = self.z*self.speed
        self.twist.angular.x = 0.0
        self.twist.angular.y = 0.0
        self.twist.angular.z = self.th*self.turn


class line_sensor_subscription(Node):
    def __init__(self):
        super().__init__("line_sensor_subscription")

        self.create_subscription(
            Int32, 'linesensor', self.line_sensor_callback, 10)
        self.subscriptions

    def line_sensor_callback(self, data):
        temp = data.data
        mijishu = 19
        temp = 1024*1024-temp-1
        global sensor_matrix
        for i in range(1, 7):
            for j in range(1, 5):
                sensor_matrix[i-1][4-j] = temp//2**mijishu
                temp = temp % 2**mijishu
                mijishu = mijishu-1
            pass
        pass
        # print(sensor_matrix)


def main(args=None):
    rclpy.init(args=args)
    node = movement()
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

        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
