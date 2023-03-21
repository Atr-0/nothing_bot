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
        '''巡线移动\n
        Parameters:
                weight - 巡线中心\n
                vel - 速度\n
                turnVel - 转弯速度 :0.4 不为0时只会转弯\n
                dis - 巡线距离\n
                yaxis - 是否y方向移动\n
                stop_weight - 计线中心\n
        '''
        # rclpy.init()
        super().__init__("movement")
        global sensor_matrix, position, direction

        self.pub = self.create_publisher(
            Twist, 'cmd_vel', 10)

        self.weight = weight
        self.speed = vel
        self.current_speed = 0
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

        # 订阅odom->base_footprint变换并传入到 position
        node_odom_sub = odom_subscription()
        rclpy.spin_once(node_odom_sub)
        # 订阅传感器数据
        node_sub = line_sensor_subscription()
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
        turn_timer = 0.0
        accel_timer = 0.0
        decel_timer = 0.0
        while rclpy.ok():
            rclpy.spin_once(node_odom_sub)
            rclpy.spin_once(node_sub)
            # 更新传感器
            temp = (list(sensor_matrix[0])+list(sensor_matrix[1]) +
                    list(sensor_matrix[2])+list(sensor_matrix[3]))
            '''y计线'''
            temp1 = (list(sensor_matrix[4])+list(sensor_matrix[5]) +
                     list(sensor_matrix[6])+list(sensor_matrix[7]))
            '''x计线'''
            # print("xxxxx",temp)
            if self.turnVel == 0.0:
                if distance > self.dis - 0.1 and (
                        temp1[7-stop_weight] +
                        temp1[8-stop_weight] +
                        temp1[(stop_weight+7)] +
                        temp1[(stop_weight+8)] >= 2) and not yaxis:
                    print("xxxxxx")
                    break
                elif distance > self.dis - 0.1 and (
                        temp[7-stop_weight] +
                        temp[8-stop_weight] +
                        temp[(stop_weight+7)] +
                        temp[(stop_weight+8)] >= 2) and yaxis:
                    print("dddddd")
                    break
                elif distance > self.dis - 0.1:
                    # 减速度
                    self.speed = self.dir * 0.1
                elif distance < self.dis - 0.1:
                    # 加速度
                    accel_timer += 0.15
                    self.speed = utils.lerp(
                        0.0, abs(vel), utils.lerp(0, 1, math.sqrt(accel_timer)))*self.dir
                    self.current_speed = self.speed
                self.y_axis_movement(
                    self.speed) if yaxis else self.x_axis_movement(self.speed)
            else:
                # 转弯
                turn_timer += 0.07
                angle_fac = utils.lerp(0, 90, turn_timer)
                if angle_fac >= 90 and (
                        temp[3] +
                        temp[11] +
                        temp1[3] +
                        temp1[11] >= 2):
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
        kp, ki, kd = 0.8, 0.0, 0.08
        hou_kp, hou_ki, hou_kd = 0.56, 0.0, 0.05

        front, back = (list(sensor_matrix[0])+list(sensor_matrix[1]),
                       (list(sensor_matrix[2]))+(list(sensor_matrix[3])))
        if self.dir == 1:
            weight = 8-self.weight
        # print(front)
        # print("bbbbbbb", back)
        if np.sum(np.array(front)) > 2:
            for i in range(len(front)):
                front[i] = 0

        if np.sum(np.array(back)) > 2:
            for i in range(len(back)):
                back[i] = 0

        feedback, houwucha = self.feedback_value(weight, front, back)
        feedback *= 0.3
        houwucha *= 0.3
        #########################
        value = 0
        value = value + (np.sum(np.array(front))if self.dir ==
                         1 else np.sum(np.array(back)))
        if value == 0:
            self.error = 0
        else:
            self.error = feedback / value
        derivative = self.error - self.previous_error
        self.integral += self.error
        corr = kp * self.error + ki * self.integral + kd * derivative
        #########################
        houvalue = 0
        houvalue = houvalue + (np.sum(np.array(back))if self.dir ==
                               1 else np.sum(np.array(front)))
        if houvalue == 0:
            self.houerror = 0
        else:
            self.houerror = houwucha / houvalue
        houderivative = self.houerror - self.houprevious_error
        self.integral += self.houerror
        houcorr = hou_kp * self.houerror + hou_ki * \
            self.integral + hou_kd * houderivative

        ans = np.sum(sensor_matrix)
        if (ans != 0):
            # self.publish_twist(v, 0, corr/-2*self.dir)
            self.publish_twist(v, houcorr/-8, corr/2)
            # print(corr*2)
            # pass
        else:
            self.publish_twist(0.1*self.dir, 0.0, 0)
        self.previous_error = self.error
        self.houprevious_error = self.houerror

    def y_axis_movement(self, v):
        global sensor_matrix
        weight = self.weight
        kp, ki, kd = 0.8, 0.0, 0.08
        hou_kp, hou_ki, hou_kd = 0.56, 0.0, 0.05

        front, back = (list(sensor_matrix[4])+list(sensor_matrix[5]),
                       (list(sensor_matrix[6]))+(list(sensor_matrix[7])))
        if self.dir == 1:
            weight = 8-self.weight
        # print(front)
        # print("bbbbbbb", back)
        if np.sum(np.array(front)) > 2:
            for i in range(len(front)):
                front[i] = 0.0

        if np.sum(np.array(back)) > 2:
            for i in range(len(back)):
                back[i] = 0.0

        feedback, houwucha = self.feedback_value(weight, front, back)
        feedback *= 0.3
        houwucha *= 0.3
        #########################
        value = 0
        value = value + (np.sum(np.array(front))if self.dir ==
                         1 else np.sum(np.array(back)))
        if value == 0:
            self.error = 0
        else:
            self.error = feedback / value
        derivative = self.error - self.previous_error
        self.integral += self.error
        corr = kp * self.error + ki * self.integral + kd * derivative
        #########################
        houvalue = 0
        houvalue = houvalue + (np.sum(np.array(back))if self.dir ==
                               1 else np.sum(np.array(front)))
        if houvalue == 0:
            self.houerror = 0
        else:
            self.houerror = houwucha / houvalue
        houderivative = self.houerror - self.houprevious_error
        self.integral += self.houerror
        houcorr = hou_kp * self.houerror + hou_ki * \
            self.integral + hou_kd * houderivative

        ans = np.sum(sensor_matrix)
        if (ans != 0):
            # self.publish_twist(v, 0, corr/-2*self.dir)
            self.publish_twist(houcorr/-10*self.dir, v, corr/2)
            # print(corr*2)
            # pass
        else:
            self.publish_twist(0.0, 0.1*self.dir, 0)
        self.previous_error = self.error
        self.houprevious_error = self.houerror

    def feedback_value(self, weight, front, back):
        '''
        计算X Y 方向的反馈值
        '''
        this_front = front
        this_back = back
        feedback = 0
        houwucha = 0
        if self.dir == -1:
            this_front = np.flipud(front)
            for i in range(0, weight):
                feedback = feedback + \
                    ((this_back[i])*abs(weight-i))
                houwucha = houwucha + \
                    ((this_front[i])*abs(weight-i))
            for i in range(weight, 8):
                feedback = feedback - \
                    ((this_back[i])*abs((i+1)-weight))
                houwucha = houwucha - \
                    ((this_front[i])*abs((i+1)-weight))
        else:
            this_back = np.flipud(back)
            for i in range(0, weight):
                feedback = feedback + \
                    ((this_front[i])*abs(weight-i))
                houwucha = houwucha + \
                    ((this_back[i])*abs(weight-i))
            for i in range(weight, 8):
                feedback = feedback - \
                    ((this_front[i])*abs((i+1)-weight))
                houwucha = houwucha - \
                    ((this_back[i])*abs((i+1)-weight))

        return feedback, houwucha

    def publish_twist(self, xvel, yvel, turn):

        self.twist.linear.x = self.x*xvel
        self.twist.linear.y = self.y*yvel
        self.twist.linear.z = 0.0
        self.twist.angular.x = 0.0
        self.twist.angular.y = 0.0
        self.twist.angular.z = 2.5*turn
        self.pub.publish(self.twist)


class simple_movement(Node):
    def __init__(self, xvel, yvel, turnVel=0.0, dis=0.0):
        '''
        不巡线的移动\n
        Parameters:
                weight - 巡线中心\n
                xvel - x速度\n
                yvel - y速度\n
                turnVel - 转弯速度\n
                dis - 发布次数\n
        '''
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
        except Exception as e:
            print(e)
            pass


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
