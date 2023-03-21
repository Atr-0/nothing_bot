import os
from utils import *
import basic
import time
import rclpy
import rclpy.action.graph
from rclpy.node import Node
from std_msgs.msg import String, Int64
import grab

rclpy.init()
motor_control_node = Node("motor_control")
motor_control_pub = motor_control_node.create_publisher(
    Int64, 'action_msg', 10)
cmd = ""


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


detect_node = Node("detect_pub")
detect_node_pub = detect_node.create_publisher(String, "shibie", 10)


def pub_detect(cmd=""):
    global detect_node_pub
    tmp = String()
    tmp.data = cmd
    detect_node_pub.publish(tmp)
    time.sleep(2)
    tmp.data = "n"
    detect_node_pub.publish(tmp)


class aqu_detect_sub(Node):
    def __init__(self):
        super().__init__("aqu_detect_sub")
        self.create_subscription(String, "detect", self.callback, 10)
        self.subscriptions

    def callback(self, data):
        self.get_logger().info('I heard: "%s"' % data.data)
        global cmd
        cmd = data.data


def count_time(func):
    def wrapper(*args, **kwargs):
        t = time.time()
        func(*args, **kwargs)
        print("运行时间:"+str((time.time()-t)//60) +
              "分"+str((time.time()-t) % 60)+"秒")
        pub_detect("f")
    return wrapper


duoji, duoji1 = "18", "13"
'''小舵机'''
huatai, shengjiang = "08", "02"
'''大舵机'''


@count_time
def main():
    global duoji, duoji1, huatai, shengjiang


if __name__ == '__main__':
    try:
        # os.system("gnome-terminal -- python3 '/home/zzb/yolov5/shibie.py'")
        # # motor_control("2", "02", "2048")
        # # motor_control("3", "08", "2048")
        # grab.grab(motor_control, huatai, shengjiang, duoji, duoji1, "closed")
        # grab.grab(motor_control, huatai, shengjiang, duoji, duoji1, "closed")
        # motor_control("3", "08", "1848")
        # time.sleep(1)

        # motor_control("2", "02", "1848")
        # time.sleep(2)
        # motor_control("2", "02", "2248")
        # time.sleep(2)
        main()
    except KeyboardInterrupt:
        pass
    finally:
        # motor_control_node.destroy_node()
        rclpy.shutdown()
