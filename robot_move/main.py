import os
from utils import *
import basic
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int64
import grab

rclpy.init()
motor_control_node = Node("motor_control")
motor_control_pub = motor_control_node.create_publisher(
    Int64, 'action_msg', 10)
motor_control_node.publishers


def motor_control(num="1", num1="1", v="0", v1="0"):
    global motor_control_pub
    temp = num+num1+v
    if num == "8":
        temp = temp+v1
    msg = Int64()

    msg.data = int(temp)
    motor_control_pub.publish(msg)
    time.sleep(0.2)


def count_time(func):
    def wrapper(*args, **kwargs):
        t = time.time()
        func(*args, **kwargs)
        print("运行时间:"+str((time.time()-t)//60) +
              "分"+str((time.time()-t) % 60)+"秒")
    return wrapper


@count_time
def main():
    duoji = "18"
    duoji1 = "13"
    # motor_control("2", "02", "148")
    # grab.grab(motor_control,duoji,duoji1,"closed")
    # time.sleep(1)
    # motor_control("2","02","1508")
    # time.sleep(10)
    # while 1:
    #     time.sleep(5)
    # time.sleep(5)
    # grab.grab(motor_control,duoji,duoji1,"spread")
    # time.sleep(3)
    # motor_control("3","08","2248")

    # time.sleep(3)
    # grab.grab(motor_control,duoji,duoji1,"closed")
    # time.sleep(3)

    # basic.movement(3, 0, 0.4, 0)
    # C
    basic.movement(3, -0.2, 0, 0.38, yaxis=False)
    time.sleep(0.5)
    basic.movement(3, -0.2, 0, 0.2, yaxis=True, stop_weight=4)
    time.sleep(0.5)
    basic.movement(3, 0, 0.4, 0)
    basic.movement(3, 0.3, 0, 0.35, yaxis=True, stop_weight=7)
    for i in range(5):
        time.sleep(0.5)
        basic.movement(6, -0.25, 0.0, 0.38, yaxis=False, stop_weight=2)
    time.sleep(0.2)
    grab.grab(motor_control, duoji, duoji1, "c")
    # A
    # basic.movement(4, 0.3, 0.0, 0.5, yaxis=True, stop_weight=3)
    # time.sleep(0.5)
    # basic.movement(5, -0.35, 0.0, 0.7, yaxis=False)
    # time.sleep(0.5)
    # basic.movement(4, -0.2, 0.0, 0.4, yaxis=True, stop_weight=6)
    # for i in range(5):
    #     time.sleep(0.5)
    #     basic.movement(6, -0.2, 0.0, 0.38, yaxis=False)
    # time.sleep(0.2)
    # grab.a_zone_grab(motor_control)


if __name__ == '__main__':
    duoji = "18"
    duoji1 = "13"
    try:
        motor_control("2", "02", "2048")
        motor_control("3", "08", "2048")
        grab.grab(motor_control, duoji, duoji1, "closed")
        time.sleep(2)
        motor_control("3", "08", "1048")
        time.sleep(2)
        motor_control("2", "02", "3048")
        time.sleep(5)
        main()
    except KeyboardInterrupt:
        pass
    finally:
        motor_control_node.destroy_node()
        rclpy.shutdown()
