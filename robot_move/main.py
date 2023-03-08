import os
from utils import *
import robot_move.basic as basic
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int32
import grab

rclpy.init()
motor_control_node = Node("motor_control")
motor_control_pub = motor_control_node.create_publisher(
    Int32, 'action_msg', 10)


def motor_control(num="1", num1="1", v="0", v1="0"):
    global motor_control_pub
    temp = num+num1+v
    if num == "8":
        temp = temp+v1
    msg = Int32()

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
    # while 1:
    motor_control("8", "09", "780", "350")
    motor_control("8", "01", "220", "350")
    motor_control("8", "09", "780", "350")
    motor_control("8", "01", "220", "350")
    time.sleep(1)
    motor_control("1", "1", "0000")
    time.sleep(5)
    basic.movement(2, 0.3, 0.0, 0.5, yaxis=True, yaxis_stop_weight=3)
    time.sleep(0.5)
    basic.movement(5, -0.35, 0.0, 0.7, yaxis=False)
    time.sleep(0.5)
    basic.movement(2, -0.2, 0.0, 0.4, yaxis=True, yaxis_stop_weight=6)
    for i in range(5):
        time.sleep(0.5)
        basic.movement(6, -0.2, 0.0, 0.38, yaxis=False)
    time.sleep(0.2)
    grab.a_zone_grab(motor_control)
    # basicMove.movement(2, 0.2, 0.0, 0.4, yaxis=True)
    # time.sleep(0.1)
    # basicMove.movement(4, 0.2, 0.0, 0.4, yaxis=False)

    # time.sleep(0.5)
    # basicMove.movement(2, 0.35, 0.0, 1.18, yaxis=True, yaxis_stop_weight=3)
    # time.sleep(0.1)
    # basicMove.movement(3, 0.0, -1.0, 0.0, yaxis=False)
    # time.sleep(0.2)
    # basicMove.movement(2, -0.2, 0.0, 0.4, yaxis=True, yaxis_stop_weight=4)
    # for i in range(5):
    #     time.sleep(0.2)
    #     basicMove.movement(6, -0.2, 0.0, 0.38, yaxis=False)
    # time.sleep(0.5)


if __name__ == '__main__':
    try:
        os.system("~/nothing_bot/src/robot_move/getPose.py")
        main()
    except KeyboardInterrupt:
        pass
    finally:
        motor_control_node.destroy_node()
        rclpy.shutdown()
