#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rclpy
from rclpy.node import Node
import rclpy.qos
from geometry_msgs.msg import Twist, Point, Vector3, Quaternion
from std_msgs.msg import Int32
from rclpy.exceptions import ROSInterruptException
import numpy as np
import tf2_ros
import rclpy.time
import time
import math
np.set_printoptions(threshold=np.inf)
sensor_matrix = np.zeros([6, 4])
position = Vector3()


class axis_movement(Node):
    integral, previous_error, error = 0, 0, 0
    kp, ki, kd = 0.83, 0.0, 0.083

    def __init__(self, vel, turnVel, dis, yaxis=False):
        rclpy.init(args=None)
        super().__init__("movement")
        global sensor_matrix, position
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.odom_frame = 'odom'
        self.base_frame = 'base_footprint'

        self.pub = self.create_publisher(
            Twist, 'cmd_vel', 10)

        self.speed = vel
        self.turn = turnVel
        self.x = float(~int(yaxis)+2)
        self.y = float(yaxis)

        self.z = 0.0
        self.th = 1.0
        self.dis = dis
        self.rate = self.create_rate(40)
        self.twist = Twist()

        node_sub = line_sensor_subscription()
        node_odom_sub = odom_subscription()

        rclpy.spin_once(node_odom_sub)
        global position
        prepos = Vector3()
        prepos.x = position.x
        prepos.y = position.y
        prepos.z = position.z
        # prepos
        distance = 0.0

        while rclpy.ok():
            rclpy.spin_once(node_odom_sub)
            # print("xxxx", position)
            # print("ppp", prepos)
            rclpy.spin_once(node_sub)
            # print(sensor_matrix)
            if distance > self.dis - 0.1 and (sensor_matrix[2][1]+sensor_matrix[2][2]+sensor_matrix[5][1]+sensor_matrix[5][2] >= 3) and not yaxis:
                break
            elif distance > self.dis - 0.1 and (sensor_matrix[0][3]+sensor_matrix[1][0]+sensor_matrix[3][0]+sensor_matrix[4][3] >= 3) and yaxis:
                break
            elif distance > self.dis - 0.1:
                self.speed = 0.25*(1.0 if self.speed > 0.0 else -1.0)

            self.y_axis_movement(
                self.speed) if yaxis else self.x_axis_movement(self.speed)

            distance = math.sqrt(pow((position.x - prepos.x), 2) +
                                 pow((position.y - prepos.y), 2))+distance
            prepos.x = position.x
            prepos.y = position.y
            prepos.z = position.z
            # print("dddd", distance)
            time.sleep(0.05)

        node_sub.destroy_node()
        node_odom_sub.destroy_node()
        self.publish_twist(0, 0)
        self.publish_twist(0, 0)

    def x_axis_movement(self, v, weight=4):
        global sensor_matrix
        front, back = sensor_matrix[0], sensor_matrix[3]
        front = np.append(front, sensor_matrix[1])
        back = np.append(back, sensor_matrix[4])

        feedback = 0
        value = 0
        f_or_d = (1.0 if self.speed > 0.0 else -1.0)
        for i in range(0, weight):
            feedback = feedback + \
                (front[i]*abs(i-weight)*f_or_d)
            feedback = feedback - \
                (back[i]*abs(weight-i)*f_or_d)
        for i in range(weight, 8):
            feedback = feedback - \
                (front[i]*abs(weight-i)*f_or_d)
            feedback = feedback + \
                (back[i]*abs(i-weight)*f_or_d)
        feedback *= 0.25
        print("f", feedback)

        value = value + np.sum(front) + np.sum(back)
        if value == 0:
            self.error = 0
        else:
            self.error = feedback / value

        derivative = self.error - self.previous_error

        self.integral += self.error

        corr = self.kp * self.error + self.ki * self.integral + self.kd * derivative
        print(corr)

        ans = np.sum(sensor_matrix)
        if (ans != 0):
            self.publish_twist(v, corr)
        else:
            self.publish_twist(0.1*f_or_d, 0)
        self.previous_error = self.error

    def y_axis_movement(self, v, weight=2):
        global sensor_matrix
        front, back = sensor_matrix[2], sensor_matrix[5]
        feedback = 0
        value = 0
        f_or_d = (1.0 if self.speed > 0.0 else -1.0)
        for i in range(0, weight):
            feedback = feedback + \
                (front[i]*abs(i-1)*f_or_d)
            feedback = feedback - \
                (back[i]*abs(1-i)*f_or_d)
        for i in range(weight, 4):
            feedback = feedback - \
                (front[i]*abs(1-i)*f_or_d)
            feedback = feedback + \
                (back[i]*abs(i-1)*f_or_d)
        feedback *= 0.25

        value = value + np.sum(front) + np.sum(back)
        # print(value)
        if value == 0:
            self.error = 0
        else:
            self.error = feedback / value

        derivative = self.error - self.previous_error

        self.integral += self.error

        corr = self.kp * self.error + self.ki * self.integral + self.kd * derivative
        # print(corr)

        ans = np.sum(sensor_matrix)
        if (ans != 0):
            self.publish_twist(v, corr)
        else:
            self.publish_twist(0.1*f_or_d, 0)
        self.previous_error = self.error

    def publish_twist(self, vel, turn):
        self.pub.publish(self.twist)
        self.twist.linear.x = self.x*vel
        self.twist.linear.y = self.y*vel
        self.twist.linear.z = self.z*vel
        self.twist.angular.x = 0.0
        self.twist.angular.y = 0.0
        self.twist.angular.z = self.th*turn


class line_sensor_subscription(Node):
    def __init__(self):
        super().__init__("line_sensor_subscription")

        self.create_subscription(
            Int32, 'linosensors', self.line_sensor_callback, rclpy.qos.qos_profile_sensor_data)
        self.subscriptions

    def line_sensor_callback(self, data):
        temp = data.data
        mijishu = 23
        temp = 2**24-temp-1
        global sensor_matrix
        for i in range(6):
            for j in range(1, 5):
                sensor_matrix[i][4-j] = temp//2**mijishu
                temp = temp % 2**mijishu
                mijishu = mijishu-1
            pass
        pass
        # print(sensor_matrix)


class odom_subscription(Node):
    def __init__(self):
        super().__init__("odom_subscription")

        self.create_subscription(
            Vector3, 'frame_listener', self.odom_callback, 10)
        self.subscriptions

    def odom_callback(self, data):
        global position
        position.x = data.x
        position.y = data.y
        position.z = data.z
        # print("!!",position)


def main(args=None):
    rclpy.init(args=args)

    node = axis_movement()
    try:
        rclpy.spin_once(node)
    except ROSInterruptException:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
