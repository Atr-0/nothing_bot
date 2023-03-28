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
    time.sleep(2.5)
    # rclpy.spin_once(aqu_detect_sub())


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
    motor_control("2", shengjiang, "1868" if not up else "1338")
    time.sleep(2)
    if up:
        time.sleep(4)

    motor_control("3", huatai, "2458")
    time.sleep(4)
    grab.grab(motor_control, huatai, shengjiang,
              duoji, duoji1, mode="spread")
    grab.grab(motor_control, huatai, shengjiang,
              duoji, duoji1, mode="closed")
    motor_control("3", huatai, "1048")
    time.sleep(4)

    motor_control("2", shengjiang, "3048")
    time.sleep(0.5)
    if up:
        time.sleep(4.5)


# duoji, duoji1 = "18", "13"
# '''小舵机'''
# huatai, shengjiang = "08", "02"
# '''大舵机'''
duoji, duoji1 = "01", "09"
'''小舵机'''
huatai, shengjiang = "08", "02"
'''大舵机'''


@count_time
def main():
    global duoji, duoji1, huatai, shengjiang
    global jieguo, item_list
    temp = []
    # pub_detect("c")
    # pub_detect("c")
    # pub_detect("c")
    # pub_detect("c")
    # rclpy.spin_once(aqu_detect_sub())
    # time.sleep(10)
    # print(jieguo)
    # while 1:
    #     pub_detect("b")
    # time.sleep(10)
    # pub_detect("n")
    ########## -A-##########
    # basic.movement(4, -0.2, 0, 0.7, True,4)
    basic.simple_movement(0, -0.2, 0, 70)
    time.sleep(0.5)
    basic.movement(4, 0.2, 0, 0.2, False)
    time.sleep(0.5)
    basic.movement(4, 0.2, 0, 0.38, False)
    time.sleep(0.5)
    basic.movement(4, 0.2, 0, 0.38, True, 6)
    # for i in range(6):
    #     pub_detect("a")
    #     time.sleep(0.5)
    #     rclpy.spin_once(detect_sub())
    #     time.sleep(0.1)
    #     temp = [int(x) for x in jieguo]
    #     print(temp)
    #     item_list[i] = temp[0]
    #     item_list[i+6] = temp[1]
    #     if i < 5:
    #         time.sleep(0.5)
    #         basic.movement(6, 0.25, 0.0, 0.35, False, 4)
    # time.sleep(0.2)
    # print(item_list)
    # grab.grab(motor_control, huatai, shengjiang,
    #           duoji, duoji1, item_list, mode="a")
    # return
    ########## -B-##########
    # num=19
    for i in range(6):
        pub_detect("b")
        time.sleep(0.5)
        rclpy.spin_once(detect_sub())
        time.sleep(0.1)
        temp = [int(x) for x in jieguo]
        print(temp)
        if len(temp) > 0:
            basic.simple_movement(
                0, 0.1, 0, 10)
            if len(temp) == 4:
                if temp[2] != 1:
                    basic.simple_movement(
                        0.1*(-1 if temp[2] == 0 else 1), 0, 0, 18)
                    time.sleep(0.5)
                print("tui down", temp[2])
                tui()

                if temp[2] != 1 and temp[1] != temp[2]:
                    time.sleep(0.5)
                    basic.movement(
                        6, -0.1*(-1 if temp[2] == 0 else 1), 0, 0.1, False)
                ################################################
                if temp[1] != 1 and temp[1] != temp[2]:
                    basic.simple_movement(
                        0.1*(-1 if temp[1] == 0 else 1), 0, 0, 18)
                    time.sleep(0.5)
                print("tui up", temp[1])
                tui(True)

                if temp[1] != 1:
                    time.sleep(0.5)
                    basic.movement(
                        6, -0.1*(-1 if temp[1] == 0 else 1), 0, 0.1, False)
                time.sleep(1)
                ################################################
            elif len(temp) == 2:
                if temp[0] == 3:
                    if temp[1] != 1:
                        basic.simple_movement(
                            0.1*(-1 if temp[1] == 0 else 1), 0, 0, 18)
                        time.sleep(0.5)

                    tui(True)

                    if temp[1] != 1:
                        time.sleep(0.5)
                        basic.simple_movement(
                            -0.1*(-1 if temp[1] == 0 else 1), 0, 0, 18)

                elif temp[1] == 4:
                    if temp[0] != 1:
                        basic.simple_movement(
                            0.1*(-1 if temp[0] == 0 else 1), 0, 0, 18)
                        time.sleep(0.5)

                    tui()

                    if temp[0] != 1:
                        time.sleep(0.5)
                        basic.simple_movement(
                            -0.1*(-1 if temp[0] == 0 else 1), 0, 0, 18)
        if i < 5:
            time.sleep(0.5)
            basic.movement(6, 0.25, 0.0, 0.35, False, 4)
    time.sleep(0.2)
    ########## -C-##########
    # basic.movement(6, -0.2, 0, 0.35, False)
    # time.sleep(0.5)
    # basic.movement(4, -0.2, 0, 0.6, True)
    # time.sleep(0.5)
    # basic.movement(4, 0.2, 0, 0.38, True)
    # time.sleep(0.5)
    # basic.movement(3, 0, 0.4, 0)
    # time.sleep(0.5)
    # basic.movement(4, 0.2, 0, 0.38, True, 6)
    # for i in range(6):

    #     pub_detect("c")
    #     time.sleep(0.5)
    #     rclpy.spin_once(detect_sub())
    #     time.sleep(0.1)
    #     temp = [int(x) for x in jieguo]
    #     print(temp)
    #     item_list[i] = np.sum(np.array(temp) == 0)
    #     item_list[i+6] = np.sum(np.array(temp) == 1)
    #     if i < 5:
    #         time.sleep(0.5)
    #         basic.movement(6, -0.25, 0.0, 0.35, False, 4)
    # time.sleep(0.2)
    # print(item_list)
    # grab.grab(motor_control, huatai, shengjiang,
    #           duoji, duoji1, item_list, mode="c")
    ########## -D-##########
    # basic.movement(6, -0.2, 0, 0.35, False)
    # time.sleep(0.5)
    # basic.movement(4, -0.2, 0, 0.78, False)
    # time.sleep(0.5)
    # basic.movement(3, 0, 0.4, 0)
    # time.sleep(0.5)
    # basic.movement(4, 0.2, 0, 0.38, True, 6)
    # for i in range(6):

    #     if i != 2 and i != 3:
    #         pub_detect("d")
    #         time.sleep(0.5)
    #         rclpy.spin_once(detect_sub())
    #         time.sleep(0.1)
    #         temp = [int(x) for x in jieguo]
    #         print(temp)
    #         if len(temp) > 2:
    #             item_list[i] = temp[1]
    #             item_list[i+6] = temp[3]
    #         elif len(temp) == 2:
    #             if temp[0] == 1:
    #                 item_list[i] = temp[1]
    #                 item_list[i+6] = -1
    #             else:
    #                 item_list[i] = -1
    #                 item_list[i+6] = temp[1]
    #         else:
    #             item_list[i] = -1
    #             item_list[i+6] = -1
    #     else:
    #         item_list[i] = 0
    #         item_list[i+6] = 0

    #     if i < 5:
    #         time.sleep(0.5)
    #         basic.movement(6, -0.25, 0.0, 0.35, False, 4)
    # time.sleep(0.2)
    # print(item_list)
    # grab.grab(motor_control, huatai, shengjiang,
    #           duoji, duoji1, item_list, mode="d")


if __name__ == '__main__':
    try:
        # os.system("gnome-terminal -- python3 '/home/zzb/yolov5/shibie.py'")
        # time.sleep(20)
        grab.grab(motor_control, huatai, shengjiang,
                  duoji, duoji1, mode="closed")
        grab.grab(motor_control, huatai, shengjiang,
                  duoji, duoji1, mode="closed")
        # while 1:
        #     grab.grab(motor_control, huatai, shengjiang,
        #             duoji, duoji1, mode="spread",)
        #     grab.grab(motor_control, huatai, shengjiang,
        #             duoji, duoji1, mode="closed")

        motor_control("3", "08", "1848")
        time.sleep(1)
        motor_control("2", "02", "1848")
        time.sleep(2)
        motor_control("2", "02", "3048")
        time.sleep(2)
        # while 1:
        #     motor_control("8", "01", "500","300")
        #     time.sleep(3)
        #     motor_control("8", "01", "800","300")
        #     time.sleep(3)
        # basic.simple_movement(0.2,0,0,50)

        # basic.movement(4, -0.2, 0, 0.8, True)
        # pub_detect("d")
        # pub_detect("b")
        # while 1:
        #     pub_detect("b")
        #     time.sleep(5)
        main()

    except KeyboardInterrupt:
        pass
    finally:
        motor_control_node.destroy_node()
        detect_node.destroy_node()
        rclpy.shutdown()
