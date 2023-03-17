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


def motor_control(num="1", num1="1", v="0", v1="0"):
    '''电机控制\n
    Parameters:
        num - 滑台舵机:"3" 升降舵机:"2" 小舵机:"8"\n
        num1 - 舵机序号 \n
        v - 舵机位置\n
        v1 - 舵机速度(只在用小舵机时有用)
    '''
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


duoji, duoji1 = "18", "13"
'''小舵机'''
huatai, shengjiang = "08", "02"
'''大舵机'''


@count_time
def main():
    global duoji, duoji1, huatai, shengjiang
    # motor_control("3", "08", "2348")
    # time.sleep(3)
    # motor_control("3", "08", "1048")
    # motor_control("2", "02", "3048")
    # time.sleep(2)
    # motor_control("2", "02", "1748")
    # time.sleep(3)
    # motor_control("2", "02", "3048")
    # while 1:
    #     grab.grab(motor_control,duoji,duoji1,"spread")
    # time.sleep(1)
    # motor_control("3","08","1848")
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
    # basic.simple_movement(0,0.2,0.1,100)
    # basic.movement(6, -0.3, 0, 0.4, yaxis=True, stop_weight=4)
    # basic.movement(6, 0.3, 0, 0.4, yaxis=True, stop_weight=4)
    # basic.movement(6, -0.2, 0, 0.4, yaxis=False)
    basic.movement(6, -0.2, 0, 0.35, yaxis=False)
    time.sleep(0.5)
    basic.movement(4, -0.2, 0, 0.55, yaxis=True, stop_weight=4)
    time.sleep(1)
    basic.movement(4, 0.2, 0, 0.55, yaxis=True, stop_weight=4)
    time.sleep(1)
    basic.movement(3, 0, 0.4, 0)
    basic.movement(4, 0.3, 0, 0.3, yaxis=True, stop_weight=7)
    for i in range(5):
        time.sleep(0.5)
        basic.movement(6, -0.25, 0.0, 0.35, yaxis=False, stop_weight=4)
    time.sleep(0.2)

    grab.grab(motor_control, huatai, shengjiang, duoji, duoji1, "c")
    time.sleep(1)
    basic.movement(6, -0.3, 0, 1.18, yaxis=False)
    time.sleep(1)
    basic.movement(3, 0, 0.4, 0)
    basic.movement(4, 0.3, 0, 0.3, yaxis=True, stop_weight=7)
    for i in range(5):
        time.sleep(0.5)
        basic.movement(6, -0.25, 0.0, 0.35, yaxis=False, stop_weight=4)
    time.sleep(0.2)
    grab.grab(motor_control, huatai, shengjiang, duoji, duoji1, "d")

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
    try:
        # motor_control("2", "02", "2048")
        # motor_control("3", "08", "2048")
        grab.grab(motor_control, huatai, shengjiang, duoji, duoji1, "closed")
        grab.grab(motor_control, huatai, shengjiang, duoji, duoji1, "closed")
        time.sleep(2)
        motor_control("3", "08", "1848")
        time.sleep(2)
        motor_control("2", "02", "2248")
        time.sleep(2)
        main()
    except KeyboardInterrupt:
        pass
    finally:
        # motor_control_node.destroy_node()
        rclpy.shutdown()
