#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
import rclpy.qos
from geometry_msgs.msg import Twist, Point, Vector3, Quaternion
from std_msgs.msg import Int32
from nav_msgs.msg import Odometry
from rclpy.exceptions import ROSInterruptException
import numpy as np
import tf2_ros
import rclpy.time
import time
import math
import utils
import PyKDL
import getPose
np.set_printoptions(threshold=np.inf)
sensor_matrix = np.zeros([6, 4])
position = Vector3()


class axis_movement(Node):
    integral, previous_error, error = 0, 0, 0
    kp, ki, kd = 1.0, 0.0, 0.1

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
        prepos = position
        distance = 0.0

        while rclpy.ok():
            rclpy.spin_once(node_sub)
            print(sensor_matrix)
            if distance > self.dis - 0.08 and (sensor_matrix[2][1]+sensor_matrix[2][2]+sensor_matrix[5][1]+sensor_matrix[5][2] >= 3) and not yaxis:
                break
            elif distance > self.dis - 0.08 and (sensor_matrix[0][3]+sensor_matrix[1][0]+sensor_matrix[3][3]+sensor_matrix[4][0] >= 4) and yaxis:
                break
            # elif distance > self.dis - 0.08:
            #     self.speed = 0.25

            self.y_axis_movement(
                self.speed) if yaxis else self.x_axis_movement(self.speed)

            time.sleep(0.02)

            rclpy.spin_once(node_odom_sub)

            distance += math.sqrt(pow((position.x - prepos.x), 2) +
                                  pow((position.y - prepos.y), 2))
            prepos = position
            print(distance)

        node_sub.destroy_node()
        node_odom_sub.destroy_node()
        self.publish_twist(0, 0)
        self.publish_twist(0, 0)

    def x_axis_movement(self, v, weight=4):
        global sensor_matrix
        front, back = sensor_matrix[0], sensor_matrix[3]
        front = np.append(front, sensor_matrix[1])
        back = np.append(back, sensor_matrix[4])
        print(front)
        feedback = 0
        value = 0
        _weight = 8-weight
        for i in range(0, weight):
            feedback = feedback + \
                (front[i]*weight*abs(i-weight))
            feedback = feedback + \
                (back[i]*_weight*abs(weight-i))
        for i in range(weight, 8):
            feedback = feedback - \
                (front[i]*_weight*abs(i-weight))
            feedback = feedback - \
                (back[i]*weight*abs(weight-i))
        feedback *= 0.1
        print(feedback)

        value = value + np.sum(front) + np.sum(back)
        print(value)
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
            self.publish_twist(0.1, 0)
        self.previous_error = self.error

    def y_axis_movement(self, v, weight=0.5):
        global sensor_matrix

        temp = np.zeros([2, 4])
        temp[0] = sensor_matrix[2]
        temp[1] = sensor_matrix[5]

        feedback = 0
        value = 0

        count_f = utils.lerp(0.0, 1.0, weight)
        print("w", count_f)
        f = utils.lerp(1.0, 1.5, count_f)
        f1 = utils.lerp(1.5, 1.0, count_f)

        print("FF", f, f1)
        for i in range(0, 2):
            for j in range(0, 4):
                if j < 2:
                    feedback = feedback + \
                        ((temp[i][j]*f)*(1+weight))
                else:
                    feedback = feedback - \
                        ((temp[i][j]*f1)*(1-weight))
        print(feedback)

        value = value + temp.sum()
        print(value)
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
            self.publish_twist(0.1, 0)
        self.previous_error = self.error

    def get_odom(self):
        try:
            self.tf_buffer.can_transform(self.odom_frame,
                                         self.base_frame,
                                         Duration(seconds=1.0))
            (trans, rot) = self.tf_buffer.lookup_transform(
                self.odom_frame, self.base_frame, rclpy.time.Time())
            print("", trans, rot)
        except (tf2_ros.TypeException):
            self.get_logger().info("TF Exception")
            return
        return (Point(*trans), self.quat_to_angle(Quaternion(*rot)))

    def quat_to_angle(self, quat):
        rot = PyKDL.Rotation.Quaternion(quat.x, quat.y, quat.z, quat.w)
        return rot.GetRPY()

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
            Odometry, 'odom/unfiltered', self.odom_callback, 10)
        self.subscriptions

    def odom_callback(self, data):
        position.x = data.pose.pose.position.x
        position.y = data.pose.pose.position.y
        position.z = data.pose.pose.position.z
        print(position)


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
