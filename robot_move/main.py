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
jieguo = ""
item_list = [0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0]


def motor_control(num="1", num1="1", v="0", v1="250"):
    '''电机控制\n
    Parameters:
        num - 滑台舵机:"3" 升降舵机:"2" 小舵机:"8"\n
        num1 - 舵机序号 \n
        v - 舵机位置\n
        v1 - 舵机速度(只在用小舵机时有用)
    '''
    global motor_control_pub
    temp = num+num1+v+v1
    # if num == "8":
    #     temp = temp+v1
    msg = Int64()

    msg.data = int(temp)
    motor_control_pub.publish(msg)

    time.sleep(0.2)


def huataidaduoji(num, v1, v2):
    motor_control(3, num, v1, v2)


def shengjiangdaduoji(num, v1, v2):
    motor_control(2, num, v1, v2)


def xiaoduoji(num, v1, v2):
    motor_control(8, num, v1, v2)


def ABduoji(num, v1, v2):
    motor_control(4, num, v1, v2)


detect_node = Node("detect_pub")
detect_node_pub = detect_node.create_publisher(String, "shibie", 10)


def pub_detect(cmd=""):
    global detect_node_pub
    tmp = String()
    tmp.data = cmd
    time.sleep(1)
    detect_node_pub.publish(tmp)
    time.sleep(0.1)


class detect_sub(Node):
    def __init__(self):
        super().__init__("obj_detect_sub")
        self.create_subscription(String, "detect", self.callback, 10)
        self.subscriptions

    def callback(self, data):
        self.get_logger().info('I heard: "%s"' % data.data)
        global jieguo
        jieguo = data.data


def count_time(func):
    def wrapper(*args, **kwargs):
        t = time.time()
        func(*args, **kwargs)
        print("运行时间:"+str((time.time()-t)//60) +
              "分"+str((time.time()-t) % 60)+"秒")
        # pub_detect("f")
    return wrapper


def tui(up=False):
    motor_control("2", shengjiang, "1808" if not up else "1248")
    time.sleep(2)
    if up:
        time.sleep(3)

    motor_control("3", huatai, "2528")
    time.sleep(3)
    motor_control("3", huatai, "1048")
    time.sleep(3)

    motor_control("2", shengjiang, "4048")
    time.sleep(2)
    if up:
        time.sleep(3)


# duoji, duoji1 = "18", "13"
# '''小舵机'''
# huatai, shengjiang = "08", "02"
# '''大舵机'''
duoji, duoji1 = "09", "10"
'''小舵机'''
huatai, shengjiang = "08", "02"
'''大舵机'''


@count_time
def main():
    global duoji, duoji1, huatai, shengjiang
    global jieguo, item_list
    temp = []
    ######### -A-##########
    basic.daoxianting(-0.01, -0.15, -0.02, dis=0.6, yaxis=True, stop_weight=4)
    time.sleep(0.5)
    basic.movement(4, 0.2, 0, 0.2, False)
    time.sleep(0.5)
    basic.movement(4, 0.2, 0, 0.38, False)
    time.sleep(0.5)
    basic.movement(4, 0.2, 0, 0.38, True, 6)
    for i in range(6):
        pub_detect("a")
        time.sleep(0.5)
        rclpy.spin_once(detect_sub())
        time.sleep(0.1)
        temp = [int(x) for x in jieguo]
        print(temp)
        if len(temp) >= 2:
            item_list[i] = temp[0]
            item_list[i+6] = temp[1]
        if i < 5:
            time.sleep(0.5)
            basic.movement(6, 0.25, 0.0, 0.35, False, 4)
    time.sleep(0.2)
    print(item_list)
    grab.grab(motor_control, huatai, shengjiang,
              duoji, duoji1, item_list, mode="a")
    ######### -B-##########
    for i in range(4):
        time.sleep(0.5)
        basic.movement(4, -0.2, 0, 0.38, True, 4)
    basic.movement(3, 0, -0.4, 0)
    time.sleep(0.5)
    basic.movement(4, 0.2, 0, 0.38, True, 6)
    for i in range(6):
        pub_detect("b")
        time.sleep(0.5)
        rclpy.spin_once(detect_sub())
        time.sleep(0.1)
        temp = [int(x) for x in jieguo]
        print(temp)
        if len(temp) > 0:
            basic.shazou(0, 0.1, 0, 25)
            time.sleep(0.5)
            if len(temp) == 4:
                if temp[2] != 1:
                    basic.shazou(0.1*(-1 if temp[2] == 0 else 1), 0.03, 0, 50)
                    time.sleep(0.5)
                print("tui down", temp[2])
                tui()

                if temp[2] != 1 and temp[1] != temp[2]:
                    time.sleep(0.5)
                    basic.daoxianting(-0.1 *
                                      (-1 if temp[2] == 0 else 1), 0.05, dis=0.05)
                ################################################
                basic.shazou(0, 0.1, 0, 8)
                time.sleep(0.5)
                if temp[1] != 1 and temp[1] != temp[2]:
                    basic.shazou(0.1*(-1 if temp[1] == 0 else 1), 0.03, 0, 50)
                    time.sleep(0.5)
                print("tui up", temp[1])
                tui(True)

                if temp[1] != 1:
                    time.sleep(0.5)
                    basic.daoxianting(-0.1 *
                                      (-1 if temp[1] == 0 else 1), 0.05, dis=0.05)
                time.sleep(1)
                ################################################
            elif len(temp) == 2:
                if temp[0] == 3:
                    if temp[1] != 1:
                        basic.shazou(
                            0.1*(-1 if temp[1] == 0 else 1), 0.03, 0, 50)
                        time.sleep(0.5)

                    tui(True)

                    if temp[1] != 1:
                        time.sleep(0.5)
                        basic.shazou(-0.1 *
                                     (-1 if temp[1] == 0 else 1), 0.03, 0, 50)

                elif temp[1] == 4:
                    if temp[0] != 1:
                        basic.shazou(
                            0.1*(-1 if temp[0] == 0 else 1), 0.03, 0, 50)
                        time.sleep(0.5)

                    tui()

                    if temp[0] != 1:
                        time.sleep(0.5)
                        basic.shazou(-0.1 *
                                     (-1 if temp[0] == 0 else 1), 0.03, 0, 50)
        if i < 5:
            time.sleep(0.5)
            basic.movement(6, 0.25, 0.0, 0.35, False, 4)
    time.sleep(0.2)
    ######### -D-##########
    basic.movement(6, -0.2, 0, 0.35, False)
    time.sleep(0.5)
    basic.movement(4, -0.2, 0, 0.6, True)
    time.sleep(0.5)
    basic.movement(4, 0.2, 0, 0.38, True)
    time.sleep(0.5)
    basic.movement(3, 0, 0.4, 0)
    time.sleep(0.5)
    basic.movement(4, 0.2, 0, 0.38, True, 6)
    for i in range(6):
        if i != 2 and i != 3:
            pub_detect("d")
            time.sleep(0.5)
            rclpy.spin_once(detect_sub())
            time.sleep(0.1)
            temp = [str(x) for x in jieguo]
            print(temp)
            if len(temp) > 3:
                item_list[i] = int(temp[1]+temp[2])
                item_list[i+6] = int(temp[4]+temp[5])
            elif len(temp) == 3:
                if temp[0] == "1":
                    item_list[i] = int(temp[1]+temp[2])
                    item_list[i+6] = -1
                else:
                    item_list[i] = -1
                    item_list[i+6] = int(temp[1]+temp[2])
            else:
                item_list[i] = -1
                item_list[i+6] = -1
        else:
            item_list[i] = 0
            item_list[i+6] = 0

        if i < 5:
            time.sleep(0.5)
            basic.movement(6, -0.25, 0.0, 0.35, False, 4)
    time.sleep(0.2)
    print(item_list)
    grab.grab(motor_control, huatai, shengjiang,
              duoji, duoji1, item_list, mode="d")

    ####### -C-##########
    basic.movement(6, -0.2, 0, 0.35, False)
    time.sleep(0.5)
    basic.movement(4, -0.2, 0, 0.78, False)
    time.sleep(0.5)
    basic.movement(3, 0, 0.4, 0)
    time.sleep(0.5)
    basic.movement(4, 0.2, 0, 0.38, True, 6)
    for i in range(6):

        pub_detect("c")
        time.sleep(0.5)
        rclpy.spin_once(detect_sub())
        time.sleep(0.1)
        temp = [int(x) for x in jieguo]
        print(temp)
        item_list[i] = np.sum(np.array(temp) == 0)
        item_list[i+6] = np.sum(np.array(temp) == 1)
        if i < 5:
            time.sleep(0.5)
            basic.movement(6, -0.25, 0.0, 0.35, False, 4)
    time.sleep(0.2)
    print(item_list)
    grab.grab(motor_control, huatai, shengjiang,
              duoji, duoji1, item_list, mode="c")


def test():
    motor_control("4", duoji1, "2048", "300")
    motor_control("4", duoji, "2048", "300")
    time.sleep(1)
    motor_control("4", duoji1, "3048", "300")
    motor_control("4", duoji, "1048", "300")
    time.sleep(1)
    motor_control("4", duoji1, "2048", "300")
    motor_control("4", duoji, "2048", "300")
    time.sleep(1)
    motor_control("4", duoji1, "3048", "300")
    motor_control("4", duoji, "1048", "300")
    time.sleep(1)

    motor_control("2", shengjiang, "1848", "250")
    time.sleep(2)
    motor_control("2", shengjiang, "3048", "250")
    time.sleep(2)

    motor_control("3", huatai, "2508", "250")
    time.sleep(3)
    motor_control("3", huatai, "1048", "250")
    time.sleep(3)

    # basic.movement(4, 0.25, 0.0, 0.35, False, 4)
    # basic.movement(4, -0.25, 0.0, 0.35, False, 4)
    # basic.movement(4, -0.25, 0.0, 0.35, True, 4)
    # basic.movement(4, 0.25, 0.0, 0.35, True, 4)
if __name__ == '__main__':
    try:
        grab.grab(motor_control, huatai, shengjiang,
                  duoji, duoji1, mode="closed")
        grab.grab(motor_control, huatai, shengjiang,
                  duoji, duoji1, mode="closed")

        motor_control("4", duoji1, "2048", "300")
        motor_control("4", duoji, "2048", "300")
        time.sleep(3)
        motor_control("4", duoji1, "3048", "300")
        motor_control("4", duoji, "1048", "300")
        time.sleep(3)

        motor_control("2", shengjiang, "1848", "250")
        time.sleep(3)
        motor_control("2", shengjiang, "3048", "250")
        time.sleep(3)
        main()

    except KeyboardInterrupt:
        pass
    finally:
        motor_control_node.destroy_node()
        detect_node.destroy_node()
        rclpy.shutdown()
