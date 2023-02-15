#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
import rclpy.qos
from geometry_msgs.msg import Twist, Point, Quaternion
from std_msgs.msg import Int32
from rclpy.exceptions import ROSInterruptException
import numpy as np
import tf2_ros
import rclpy.time
import time
from math import sqrt
import PyKDL
np.set_printoptions(threshold=np.inf)

sensor_matrix = np.zeros([5, 4])

kp, kd, ki = 0.67, 0.063, 0
corr = 0.0
sum, wsum = 0, 0


class movement(Node):
    derr, sum_err, err, preErr = 0, 0, 0, 0

    def __init__(self, vel, turnVel, dis):
        rclpy.init(args=None)
        super().__init__("movement")
        global sensor_matrix
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.odom_frame = 'odom'
        self.tf_buffer.can_transform('odom',
                                     'base_footprint',
                                     Duration(seconds=1.0))
        self.base_frame = 'base_footprint'

        self.pub = self.create_publisher(
            Twist, 'cmd_vel', 10)
        self.speed = vel
        self.turn = turnVel
        self.x = 0.0
        self.y = 1.0
        self.z = 0.0
        self.th = 1.0
        self.rate = self.create_rate(40)
        self.twist = Twist()
        position = Point()

        # (position, rotation) = self.get_odom()
        (position, rotation) = 0, 0

        prepos = position

        node_sub = line_sensor_subscription()
        distance = 0
        while rclpy.ok():
            rclpy.spin_once(node_sub)
            print(sensor_matrix)
            if distance > dis - 0.08 and (sensor_matrix[2][2]+sensor_matrix[2][1]+sensor_matrix[2][0]+sensor_matrix[2][3] >= 4):
                break
            elif distance > dis - 0.08:
                self.speed = 0.25

            # 直行
            self.zhixing(sensor_matrix, self.speed, 3)
            # 发布一次Twist消息 和 sleep 1秒
            time.sleep(0.02)

            # 给出正确的姿态信息（位置和转角）
            (position, rotation) = self.get_odom()

            # 计算相对于开始位置的欧几里得距离（即位移）
            distance = sqrt(pow((position.x - prepos.x), 2) +
                            pow((position.y - prepos.y), 2))+distance
            prepos = position
            print(distance)
            # 超过每格的长度，并且计线计到跳出while

        node_sub.destroy_node()

        self.twist.linear.x = 0.0
        self.twist.linear.y = 0.0
        self.twist.linear.z = 0.0
        self.twist.angular.x = 0.0
        self.twist.angular.y = 0.0
        self.twist.angular.z = 0.0

        self.pub.publish(self.twist)

    def zhixing(self, sensor_matrix, v, zhongxin):
        preErr = self.err
        temp = sensor_matrix[0]
        temp = np.append(temp, sensor_matrix[1])
        wsum = float(0)
        sum = 0
        # wsum = (2) * temp[zhongxin-1] + (0.5) * temp[zhongxin]  + (-0.5) * temp[zhongxin+1] + (-2) * temp[zhongxin+2]
        # sum = temp[zhongxin-1] + temp[zhongxin] +temp[zhongxin+1]+ temp[zhongxin+2]
        for i in range(0, zhongxin+1):
            wsum = wsum+1.5/(float(abs(zhongxin)))*(zhongxin-i)*temp[i]
        for i in range(zhongxin+1, 8):
            wsum = wsum-1.5/(float(abs(8-zhongxin)))*(i-zhongxin)*temp[i]
        for i in range(0, 8):
            sum = sum+temp[i]
        self.err = wsum / sum
        if sum == 0:
            self.err = 0
        derr = self.err - preErr
        self.sum_err += self.err
        corr = kp * self.err + kd * derr + ki * self.sum_err
        ans = np.sum(sensor_matrix)
        if (ans != 0):
            self.publish_twist(v, corr)
        else:
            self.publish_twist(0.1, 0)

    def get_odom(self):
        # Get the current transform between the odom and base frames
        try:
            (trans, rot) = self.tf_buffer.lookup_transform(
                self.odom_frame, self.base_frame, rclpy.time.Time())
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
            Int32, 'topic', self.line_sensor_callback, rclpy.qos.qos_profile_sensor_data)
        self.subscriptions

    def line_sensor_callback(self, data):
        temp = data.data
        mijishu = 19
        temp = 1024*1024-temp-1
        global sensor_matrix
        for i in range(1, 6):
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
        rclpy.spin_once(node)
    except ROSInterruptException:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
