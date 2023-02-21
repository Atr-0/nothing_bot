#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from numpy import double
import rclpy
from rclpy.node import Node
import rclpy.qos
from geometry_msgs.msg import Vector3, Twist
from std_msgs.msg import Float64
from rclpy.time import Time
import tf2_ros
import utils
from rclpy.duration import Duration


class getPose(Node):
    def __init__(self):
        super().__init__('tf2_frame_listener')
        self.publisher_ = self.create_publisher(Vector3, 'frame_listener', 10)
        self.position_vector = Vector3()
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.timer = self.create_timer(0.05, self.timer_callback)

    def timer_callback(self):
        self.tf_buffer.can_transform('odom',
                                     'base_footprint',
                                     Duration(seconds=1.0))
        if rclpy.ok():
            t = self.tf_buffer.lookup_transform(
                'odom',
                'base_footprint',
                Time()).transform
            data = Vector3()
            data.x = t.translation.x
            data.y = t.translation.y
            data.z = t.translation.z
            self.publisher_.publish(data)
            print(data)

        else:
            print('can not transform')


def main():
    rclpy.init()
    node = getPose()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
