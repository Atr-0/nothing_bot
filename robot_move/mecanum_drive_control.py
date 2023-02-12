#! /usr/bin/env python
# -*- coding: utf-8 -*-

import rclpy
from rclpy.exceptions import ROSInterruptException
from rclpy.node import Node
import rclpy.logging

from geometry_msgs.msg import Twist
from std_msgs.msg import Int16MultiArray
from geometry_msgs.msg import Twist


from mecanum_driver import Controller


class ControllerNode(Node):

    def __init__(self):
        super().__init__("mecanum_drive_controller")
        self.node_name = self.get_name()

        self.controller = Controller()
        self.linearXVelocity = 0.0
        self.linearYVelocity = 0.0
        self.angularVelocity = 0.0
        self.wheels_to_send = Int16MultiArray()

        self.get_node_parameter()

        self.Pub = self.create_publisher('wheels_desired_rate',
                                         Int16MultiArray, 10)
        self.get_logger().info("{0} started".format(self.node_name))

        self.create_subscription("~/cmd_vel", Twist, self.twistCallback)

        self.rate = self.create_rate(self.get_parameter("rate", 10.0))

        self.last_twist_time = self.get_clock().now()

        while not rclpy.shutdown(self):
            self.publish()
            self.rate.sleep()

    def get_node_parameter(self):
        self.parameters = {
            "ticksPerMeter": 10000,
            "wheelSeparation": 0.2,
            "wheelSeparationLength": 0.2,
            "maxMotorSpeed": 3000,
            "timeout": None,
        }

        for key in self.parameters.keys():
            self.declare_parameter(key, self.parameters[key])
            self.parameters[key] = self.get_parameter(key).value
            self.get_logger().info(
                f"Publish ros2 parameter, {key}: {self.parameters[key]}")

        self.controller.setTicksPerMeter(self.parameters["ticksPerMeter"])
        self.controller.setWheelSeparation(self.parameters["wheelSeparation"])
        self.controller.setWheelSeparationLength(
            self.parameters.get("wheelSeparationLength"))
        self.controller.setMaxMotorSpeed(self.parameters["maxMotorSpeed"])

    def publish(self):
        if self.get_clock().now() - self.last_twist_time < self.timeout:
            speeds = self.controller.getSpeeds(self.linearXVelocity, self.linearYVelocity,
                                               self.angularVelocity)

            self.wheels_to_send.data = [int(speeds.frontLeft), int(
                speeds.frontRight), int(speeds.rearLeft), int(speeds.rearRight)]
            self.Pub.publish(self.wheels_to_send)
        else:
            self.wheels_to_send.data = [0, 0, 0, 0]
            self.Pub.publish(self.wheels_to_send)

    def twistCallback(self, twist):
        twist = Twist(twist)
        self.linearXVelocity = twist.linear.x
        self.linearYVelocity = twist.linear.y
        self.angularVelocity = twist.angular.z
        # print("%d,%d" % (self.linearVelocity, self.angularVelocity))
        self.last_twist_time = self.get_clock().now()


def main(args=None):
    rclpy.init(args=args)
    node = ControllerNode()
    try:
        rclpy.spin(node)
    except ROSInterruptException:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown(node)


if __name__ == '__main__':
    main()
