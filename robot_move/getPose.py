#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rclpy
from rclpy.node import Node
import rclpy.qos
from geometry_msgs.msg import Twist
import time
from utils import getRobotPos, distance
from tf2_ros import transform_listener, TypeException
from rclpy.time import Time
import tf2_ros
from rclpy.duration import Duration


class getPose(Node):
    def __init__(self):
        super().__init__('tf2_frame_listener')

        self.tf_buffer = tf2_ros.Buffer()

        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.timer = self.create_timer(1.0, self.on_timer)

    def on_timer(self):
        time.sleep(0.2)
        self.tf_buffer.can_transform('map',
                                     'base_link',
                                     Duration(seconds=1.0))

        if rclpy.ok():
            t = self.tf_buffer.lookup_transform(
                'map',
                'base_link',
                Time())

            import numpy as np
            msg = np.array([t.transform.translation.x,
                            t.transform.translation.y,
                            t.transform.translation.z,
                            t.transform.rotation.x,
                            t.transform.rotation.y,
                            t.transform.rotation.z,
                            t.transform.rotation.w])
            print(msg)
            np.savetxt("/tmp/pose.txt",
                       msg, fmt='%f', delimiter=',')
            # b = np.loadtxt('a.txt', delimiter=',')

            t = None
        else:
            print('can not transform')

        # self.publisher.publish(msg)


if __name__ == '__main__':
    rclpy.init()
    node = getPose()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()
