#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rclpy
from rclpy.node import Node
import rclpy.qos
from geometry_msgs.msg import Twist, Point, Vector3, Quaternion, Pose
from std_msgs.msg import Int64
from nav_msgs.msg import Odometry
from rclpy.exceptions import ROSInterruptException
import numpy as np
import rclpy.time
import time
import math
import utils
np.set_printoptions(threshold=np.inf)

direction = 0
sensor_matrix = np.zeros([8, 4])
position = Vector3()


class movement(Node):
    integral, previous_error, error = 0.0, 0.0, 0.0
    houprevious_error, houerror = 0.0, 0.0

    def __init__(self, weight, vel, turnVel=0.0, dis=0.4, yaxis=False, stop_weight=3):
        # rclpy.init()
        super().__init__("movement")
        global sensor_matrix, position, direction

        self.pub = self.create_publisher(
            Twist, 'cmd_vel', 10)

        self.weight = weight
        self.speed = vel
        self.dir = (1.0 if self.speed > 0.0 else -1.0)
        self.turnVel = turnVel

        self.x = 1.0
        # self.y = float(yaxis)
        self.y = 1.0
        self.z = 0.0
        self.th = 1.0
        self.dis = dis

        self.rate = self.create_rate(20)
        self.twist = Twist()

        node_sub = line_sensor_subscription()
        node_odom_sub = odom_subscription()
        # 订阅odom->base_footprint变换并传入到 position
        rclpy.spin_once(node_odom_sub)
        # 订阅传感器数据
        rclpy.spin_once(node_sub)

        global position
        prepos = Vector3()
        prepos.x = position.x
        prepos.y = position.y
        prepos.z = position.z
        distance = 0.0
        # while 1:
        #     rclpy.spin_once(node_sub)
        #     print(sensor_matrix)
        #     time.sleep(0.05)
        turm_timer = 0.0
        speed_timer = 0.0

        while rclpy.ok():
            rclpy.spin_once(node_odom_sub)
            rclpy.spin_once(node_sub)

            if self.turnVel == 0.0:
                speed_timer += 0.1
                # 更新传感器
                temp = (list(sensor_matrix[0])+list(sensor_matrix[1]) +
                        list(sensor_matrix[2])+list(sensor_matrix[3]))
                '''y计线'''
                temp1 = list(sensor_matrix[4])+list(sensor_matrix[5])
                '''x计线左'''
                temp2 = list(sensor_matrix[6])+list(sensor_matrix[7])
                '''x计线右'''
                flag = temp1[2]+temp1[3] + \
                    temp2[4]+temp2[5]
                if distance > self.dis - 0.1 and (flag >= 2) and not yaxis:
                    print("xxxxxx")
                    break
                elif distance > self.dis - 0.1 and (
                        temp[stop_weight] +
                        temp[stop_weight+1] +
                        temp[stop_weight+8] +
                        temp[stop_weight+7] >= 2) and yaxis:
                    print("dddddd")
                    break
                elif distance > self.dis - 0.2:
                    self.speed = 0.2*self.dir
                elif distance < self.dis - 0.1:
                    self.speed = utils.lerp(
                        0.0, abs(vel), utils.lerp(0, 1, math.sqrt(speed_timer)))*self.dir
                self.y_axis_movement(
                    self.speed) if yaxis else self.x_axis_movement(self.speed)
            else:
                turm_timer += 0.05
                angle_fac = utils.lerp(0, 90, turm_timer)
                if angle_fac >= 90 and (
                        sensor_matrix[0][self.weight] +
                        sensor_matrix[1][3-self.weight] +
                        sensor_matrix[2][self.weight] +
                        sensor_matrix[3][3-self.weight] >= 3):
                    print("ttttttt")
                    break
                self.publish_twist(0.0, 0.0, self.turnVel)
            # 更新距离
            distance = math.sqrt(pow((position.x - prepos.x), 2) +
                                 pow((position.y - prepos.y), 2))+distance
            prepos.x = position.x
            prepos.y = position.y
            prepos.z = position.z
            time.sleep(0.05)
        # 重置状态
        self.publish_twist(0, 0, 0)
        time.sleep(0.01)
        self.publish_twist(0, 0, 0)
        self.integral, self.previous_error, self.error = 0.0, 0.0, 0.0
        self.houprevious_error, self.houerror = 0.0, 0.0
        self.speed = 0.0
        self.turnVel = 0.0
        self.x = 0.0
        self.y = 0.

        self.z = 0.0
        self.th = 0.0
        self.dis = 0.0
        # 销毁节点
        self.destroy_node()
        node_sub.destroy_node()
        node_odom_sub.destroy_node()

    def x_axis_movement(self, v):
        global sensor_matrix
        weight = self.weight
        kp, ki, kd = 0.8, 0.0, 0.05
        hou_kp, hou_ki, hou_kd = 0.56, 0.0, 0.05
        front, back = (list(sensor_matrix[0])+list(sensor_matrix[1]),
                       (list(sensor_matrix[2]))+(list(sensor_matrix[3])))
        if self.speed < 0.0:
            front, back = back, front
        print(front)
        print("bbbbbbb", back)
        if np.sum(front) > 3:
            for i in range(len(front)):
                front[i] = 0.0

        if np.sum(back) > 3:
            for i in range(len(back)):
                back[i] = 0.0

        feedback, houwucha = self.feedback_value(weight, front, back)
        feedback *= 0.4
        houwucha *= 0.4

        corr = self.pid(kp, ki, kd, front, back, feedback)
        houcorr = self.pid(
            hou_kp, hou_ki, hou_kd, front, back, houwucha, True)
        # print(houcorr)

        ans = np.sum(sensor_matrix)
        if (ans != 0):
            self.publish_twist(v, houcorr/-4, corr*self.dir/-2)
            # self.publish_twist(v, houcorr/-2, corr/2)
            # print(corr*2)
            # pass
        else:
            self.publish_twist(0.1*self.dir, 0.0, 0)
        self.previous_error = self.error
        self.houprevious_error = self.houerror

    def y_axis_movement(self, v):
        global sensor_matrix
        weight = self.weight
        kp, ki, kd = 0.8, 0.0, 0.06
        hou_kp, hou_ki, hou_kd = 0.56, 0.0, 0.05
        front, back = (list(sensor_matrix[4])+list(sensor_matrix[5]),
                       list(sensor_matrix[6])+list(sensor_matrix[7]))
        if self.dir == -1:
            front, back = back, front
        if np.sum(front) > 3:
            for i in range(len(front)):
                front[i] = 0.0

        if np.sum(back) > 3:
            for i in range(len(back)):
                back[i] = 0.0

        feedback, houwucha = self.feedback_value(weight, front, back)
        feedback *= 0.4
        houwucha *= 0.4

        corr = self.pid(kp, ki, kd, front, back, feedback)
        houcorr = self.pid(
            hou_kp, hou_ki, hou_kd, front, back, houwucha, True)
        # print(houcorr)

        ans = np.sum(sensor_matrix)
        if (ans != 0):
            self.publish_twist(houcorr/-4, v, (corr*self.dir)/2)
            # print(corr/-2)
        else:
            self.publish_twist(0.0, 0.1*self.dir, 0)
        self.previous_error = self.error
        self.houprevious_error = self.houerror

    def feedback_value(self, weight, front, back):
        '''
        计算X Y 方向的反馈值
        '''
        feedback = 0
        houwucha = 0
        for i in range(0, weight):
            feedback = feedback + \
                ((front[i])*abs(weight-i))
            houwucha = houwucha + \
                ((back[i])*abs(weight-i))
        for i in range(weight, 8):
            feedback = feedback - \
                ((front[i])*abs((i+1)-weight))
            houwucha = houwucha - \
                ((back[i])*abs((i+1)-weight))

        return feedback, houwucha

    def pid(self, kp, ki, kd, front, back, feedback, hou=False):
        error = 0
        value = 0
        if hou:
            previous_error = self.houprevious_error
            value = value + np.sum(np.array(back))
        else:
            previous_error = self.previous_error
            value = value + np.sum(np.array(front))

        if value == 0:
            error = 0
        else:
            error = feedback / value
        derivative = error - previous_error
        self.integral += error
        corr = kp * error + ki * self.integral + kd * derivative

        if hou:
            self.houerror = error
        else:
            self.error = error
        return corr

    def publish_twist(self, xvel, yvel, turn):

        self.twist.linear.x = self.x*xvel
        self.twist.linear.y = self.y*yvel
        self.twist.linear.z = 0.0
        self.twist.angular.x = 0.0
        self.twist.angular.y = 0.0
        self.twist.angular.z = 2.0*turn
        self.pub.publish(self.twist)


class simple_movement(Node):
    def __init__(self, xvel, yvel, turnVel=0.0, dis=0.0):
        # rclpy.init(args=None)
        super().__init__("simple_movement")
        self.pub = self.create_publisher(
            Twist, 'cmd_vel', 10)
        self.x = 1.0
        self.y = 1.0
        self.dis = dis
        self.rate = self.create_rate(20)
        self.twist = Twist()
        while rclpy.ok() and self.dis > 0:
            self.publish_twist(xvel, yvel, turnVel)
            self.dis = self.dis - 1
            time.sleep(0.05)
        self.destroy_node()

    def publish_twist(self, xvel, yvel, turn):
        self.twist.linear.x = self.x*xvel
        self.twist.linear.y = self.y*yvel
        self.twist.linear.z = 0.0
        self.twist.angular.x = 0.0
        self.twist.angular.y = 0.0
        self.twist.angular.z = 2.0*turn
        self.pub.publish(self.twist)


class line_sensor_subscription(Node):
    def __init__(self):
        super().__init__("line_sensor_subscription")

        self.create_subscription(
            Int64, 'linosensors', self.line_sensor_callback, rclpy.qos.qos_profile_sensor_data)
        self.subscriptions

    def line_sensor_callback(self, data):
        try:
            temp = data.data
            mijishu = 31
            temp = 2**32-temp-1
            global sensor_matrix
            for i in range(8):
                for j in range(4):
                    sensor_matrix[i][3-j] = temp//2**mijishu
                    temp = temp % 2**mijishu
                    mijishu = mijishu-1
                pass
            pass
        except Exception:
            print("e")
            pass
        # reverse_2, reverse_3, reverse_5, = (
        #     np.flipud(sensor_matrix[2]),
        #     np.flipud(sensor_matrix[3]),
        #     np.flipud(sensor_matrix[5]))
        # sensor_matrix[2] = reverse_2
        # sensor_matrix[3] = reverse_3
        # sensor_matrix[5] = reverse_5
        # print(sensor_matrix)


class odom_subscription(Node):
    def __init__(self):
        super().__init__("odom_subscription")

        # self.create_subscription(
        #     Vector3, 'frame_listener', self.odom_callback, 10)
        self.create_subscription(
            Odometry, 'odom/unfiltered', self.odom_callback, 10)
        self.subscriptions

    def odom_callback(self, data):
        global position
        position.x = data.pose.pose.position.x
        position.y = data.pose.pose.position.y
        position.z = data.pose.pose.position.z
        # print("!!",position)
