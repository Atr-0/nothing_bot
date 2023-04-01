from utils import *
import basic
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int32


a_zone_item_list = [0, 2, 0, 2, 1, 2,
                    0, 1, 1, 1, 0, 2]
'''
1 2 3 4 5 6
'''

c_zone_item_list = [1, 2, 0, 0, 0, 1,
                    2, 2, 0, 1, 1, 2]
'''
1 2 3 4 5 6
'''
d_zone_item_list = [2, 1, 0, 0, 3, -1,
                    -1, -1, 0, 0, -1, 4]
'''
1 2 3 4 5 6
'''


class grab():

    def __init__(self, func, huatai, shengjiang, duoji, duoji1, item_list=None, mode=None, outdis="2248", updis="1538"):
        '''抓取
        Parameters:
                huatai - 滑台舵机序号\n
                shengjiang - 升降舵机序号\n
                duoji - 小舵机序号\n
                duoji1 - 小舵机序号\n
                mode - 抓取模式:\n
                        "a" | "b" | "c" :抓取的区域\n
                        "spread" | "closed" :爪子打开 | 爪子闭合 \n
                        "grab_below" | "graba_above" :抓下面 | 抓上面 \n
                        "push_below" | "push_above" :放下面 | 放上面 \n
                huataijuli - 滑台伸出距离\n
                shangjiangjuli - 升降上升距离\n
        '''
        global a_zone_item_list, c_zone_item_list, d_zone_item_list
        self.duoji = duoji
        self.duoji1 = duoji1
        self.huatai = huatai
        self.shengjiang = shengjiang
        self.func = func
        match mode:
            case "a":
                a_zone_item_list = item_list
                self.a_zone_grab()
            case "c":
                c_zone_item_list = item_list
                self.c_zone_grab()
            case "d":
                d_zone_item_list = item_list
                self.d_zone_grab()
            case "spread":
                self.spread_claw()
            case "closed":
                self.closed_claw()
            case "grab_below":
                self.grab_below(outdis)
            case "graba_above":
                self.grab_above(updis, outdis)
            case "push_below":
                self.push_below(outdis)
            case "push_above":
                self.push_above(updis, outdis)

    def func(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def a_zone_grab(self, pos=5):
        global a_zone_item_list
        zone_num = 2 if (pos == 5 or pos == 4) else (
            1 if (pos == 3 or pos == 2) else 0)
        grab_pos, push_pos, target_zone = -1, -1, -1
        range_value = range(5, -1, -1)
        if pos < 3:
            range_value = range(0, 6)

        for i in range_value:
            for j in range(1, -1, -1):
                if a_zone_item_list[i+(j*6)] == zone_num and grab_pos == -1 and (i != zone_num+(zone_num+1) and i != zone_num+zone_num):
                    grab_pos = i+(j*6)
                    target_zone = 2 if (normalize_pos(grab_pos) == 5 or normalize_pos(grab_pos) == 4) else (
                        1 if (normalize_pos(grab_pos) == 3 or normalize_pos(grab_pos) == 2) else 0)
                    print(grab_pos, "xxxxxxxxxxxxxxx")
        # print(grab_pos)
        for i in range(zone_num+(zone_num+1), zone_num+zone_num-1, -1):
            for j in range(1, -1, -1):
                if a_zone_item_list[i+(j*6)] == target_zone and push_pos == -1:
                    push_pos = i+(j*6)
                    print(push_pos, "yyyyyyyyyyyy")
        # print(push_pos)
        to_dis = (pos-normalize_pos(push_pos))
        to_grab_dis = normalize_pos(push_pos)-normalize_pos(grab_pos)
        if grab_pos == -1:
            if pos > 0:
                basic.movement(6, -0.2,
                               0, 0.39, False, stop_weight=4)
                return self.a_zone_grab(pos-1)
            else:
                return

        ##### grab#####
        time.sleep(0.5)
        if to_dis != 0:
            basic.movement(6, -0.2*(to_dis/abs(to_dis)),
                           0, 0.39*abs(to_dis), False, stop_weight=4)
        basic.simple_movement(0.0, 0.1, 0, 8)
        if push_pos < 6:
            self.func("2", self.shengjiang, "1348")
            time.sleep(10)
            self.__spread_claw__()
            time.sleep(1)
            self.func("2", self.shengjiang, "2188")
            time.sleep(2)
            self.__closed_claw__()
            self.func("2", self.shengjiang, "4048")
            time.sleep(10)
        else:
            self.func("2", self.shengjiang, "1828")
            time.sleep(2)
            self.__spread_claw__()
            time.sleep(1)
            self.func("2", self.shengjiang, "3048")
            time.sleep(2)
            self.__closed_claw__()
        ##### push#####
        time.sleep(0.5)
        if to_grab_dis != 0:
            basic.movement(6, -0.2*(to_grab_dis/abs(to_grab_dis)),
                           0, 0.39*abs(to_grab_dis), False, stop_weight=4)
        time.sleep(0.5)
        basic.simple_movement(0.0, 0.1, 0, 8)
        time.sleep(0.5)
        basic.simple_movement(-0.1, 0, 0, 19)
        if grab_pos < 6:
            self.func("2", self.shengjiang, "1408")
            time.sleep(10)
            self.__spread_claw__()
            self.func("2", self.shengjiang, "1998")

            time.sleep(1)
            basic.movement(6, 0.1, 0, 0.1, False, 4)
            time.sleep(1)

            self.func("2", self.shengjiang, "2198")
            time.sleep(2)
            self.__closed_claw__()
            self.func("2", self.shengjiang, "4048")
            time.sleep(10)
        else:
            self.func("2", self.shengjiang, "1948")
            time.sleep(1.5)
            self.__spread_claw__()
            self.func("2", self.shengjiang, "1948")

            time.sleep(1)
            basic.movement(6, 0.1, 0, 0.1, False, 4)
            time.sleep(1)

            self.func("2", self.shengjiang, "3048")
            time.sleep(2.5)
            self.__closed_claw__()

        ##### push#####
        if to_grab_dis != 0:
            basic.movement(6, 0.2*(to_grab_dis/abs(to_grab_dis)),
                           0, 0.39*abs(to_grab_dis), False, stop_weight=4)
        time.sleep(0.5)
        basic.simple_movement(0.0, 0.1, 0, 8)
        if push_pos < 6:
            self.func("2", self.shengjiang, "1388")
            time.sleep(10)
            self.__spread_claw__()
            self.func("2", self.shengjiang, "1948")
            time.sleep(2)
            self.__closed_claw__()
            self.func("2", self.shengjiang, "4048")
            time.sleep(10)
        else:
            self.func("2", self.shengjiang, "1948")
            time.sleep(2)
            self.__spread_claw__()
            self.func("2", self.shengjiang, "1948")
            time.sleep(2)
            self.__closed_claw__()
            self.func("2", self.shengjiang, "3048")
            time.sleep(3)
        ###############
        a_zone_item_list[grab_pos] = target_zone
        a_zone_item_list[push_pos] = zone_num
        print(a_zone_item_list)
        return self.a_zone_grab(pos=normalize_pos(push_pos))

    def c_zone_grab(self, pos=5):
        global c_zone_item_list
        grab_pos, push_pos = -1, -1
        range_value = range(5, -1, -1)
        if pos < 3:
            range_value = range(0, 6)

        for i in range_value:
            for j in range(1, -1, -1):
                if c_zone_item_list[i+(j*6)] == 2 and grab_pos == -1:
                    grab_pos = i+(j*6)
                if c_zone_item_list[i+(j*6)] == 0 and push_pos == -1:
                    push_pos = i+(j*6)

        if grab_pos == -1 or push_pos == -1:
            # if abs(5-pos) != 0:
            #     basic.movement(6, -0.25,
            #                    0, 0.39*abs(5-pos), False, stop_weight=4)
            return
        to_grab_dis = (pos-normalize_pos(grab_pos))
        to_push_dis = (normalize_pos(grab_pos)-normalize_pos(push_pos))

        time.sleep(0.5)
        if to_grab_dis != 0:
            basic.movement(6, 0.2*(to_grab_dis/abs(to_grab_dis)),
                           0, 0.39*abs(to_grab_dis), False, stop_weight=4)
        time.sleep(0.5)
        ##### grab#####
        basic.simple_movement(0.0, 0.1, 0, 10)
        if grab_pos < 6:
            self.grab_above()
            self.func("2", self.shengjiang, "3048")
            time.sleep(5)
        else:
            self.grab_below()
        c_zone_item_list[grab_pos] = 1
        ###############
        time.sleep(0.5)
        if to_push_dis != 0:
            basic.movement(6, 0.2*(to_push_dis/abs(to_push_dis)),
                           0, 0.39*abs(to_push_dis), False, stop_weight=4)
        time.sleep(0.5)
        ##### push#####
        basic.simple_movement(0.0, 0.1, 0, 10)
        if push_pos < 6:
            self.push_above()
            self.func("2", self.shengjiang, "3048")
            time.sleep(5)
        else:
            self.push_below()
        c_zone_item_list[push_pos] = 1
        ###############

        return self.c_zone_grab(normalize_pos(push_pos))

    def d_zone_grab(self, pos=5):
        global d_zone_item_list
        item = {
            "wangzai": 1,
            "wanglaoji": 2,
            "xuehua": 3,
            "ADgai": 4,
        }
        '''
        3 1
        4 2
        '''
        grab_pos = -1
        goal_item = -1
        item_pos = 1
        range_value = range(5, -1, -1)
        if pos < 3:
            range_value = range(0, 6)
        for i in range_value:
            if i == 3 or i == 2:
                continue
            for j in range(1, -1, -1):
                for d, k in item.items():
                    if int(d_zone_item_list[i+(j*6)]//10) % 10 == k and grab_pos == -1:
                        grab_pos = i+(j*6)
                        push_pos = 2 if (k == 2 or k == 4) else 3
                        goal_item = k
                        item_pos = d_zone_item_list[i+(j*6)] % 10
                        break
        if grab_pos == -1:
            basic.movement(6, -0.2,
                           0, 0.39*(5-pos), False, stop_weight=4)
            return
        to_grab_dis = (pos-normalize_pos(grab_pos))
        to_push_dis = (normalize_pos(grab_pos) -
                       normalize_pos(push_pos))
        if to_grab_dis != 0:
            basic.movement(6, 0.2*(to_grab_dis/abs(to_grab_dis)),
                           0, 0.39*abs(to_grab_dis), False, stop_weight=4)
        time.sleep(0.5)
        ##### grab#####
        basic.simple_movement(0.0, 0.1, 0, 10)
        if item_pos != 1:
            if item_pos == 0:
                basic.simple_movement(0.1, 0, 0, 20)
            else:
                basic.simple_movement(-0.1, 0, 0, 20)
        if grab_pos < 6:
            self.grab_above("1538")
            self.func("2", self.shengjiang, "3048")
            time.sleep(5)
        else:
            self.grab_below()
        if item_pos != 1:
            if item_pos == 0:
                basic.movement(6, -0.1, 0, 0.05, False)
            else:
                basic.movement(6, 0.1, 0, 0.05, False)

        d_zone_item_list[grab_pos] = -1
        ###############
        time.sleep(0.5)
        if to_push_dis != 0:
            basic.movement(6, 0.2*(to_push_dis/abs(to_push_dis)),
                           0, 0.39*abs(to_push_dis), False, stop_weight=4)
        time.sleep(0.5)
        ##### push#####
        basic.simple_movement(0.0, 0.1, 0, 10)
        if goal_item == 1 or goal_item == 2:
            self.push_above()
            self.func("2", self.shengjiang, "3048")
            time.sleep(5)
        else:
            self.push_below()
        d_zone_item_list[push_pos + (6 if goal_item <= 2 else 0)] = goal_item
        ###############
        print(d_zone_item_list)
        return self.d_zone_grab(push_pos)

    def grab_below(self, outdis="2288"):
        self.spread_claw()
        self.func("3", self.huatai, outdis)
        time.sleep(2)
        self.closed_claw()
        self.func("3", self.huatai, "1748")
        time.sleep(2)

    def grab_above(self, updis="1538", outdis="2288"):
        self.func("2", self.shengjiang, updis)
        time.sleep(5)
        self.spread_claw()
        self.func("3", self.huatai, outdis)
        time.sleep(2)
        self.closed_claw()
        self.func("3", self.huatai, "1748")
        time.sleep(2)

    def push_below(self, outdis="2288"):
        self.func("2", self.shengjiang, "1998")
        time.sleep(1)
        self.func("3", self.huatai, outdis)
        time.sleep(2)
        self.spread_claw()

        self.func("2", self.shengjiang, "1948")
        time.sleep(2)
        self.func("3", self.huatai, "1748")
        time.sleep(2)

        self.closed_claw()
        self.func("2", self.shengjiang, "2548")
        time.sleep(0.2)

    def push_above(self, updis="1538", outdis="2288"):
        self.func("2", self.shengjiang, str(int(updis)-50))
        time.sleep(5)

        self.func("3", self.huatai, outdis)
        time.sleep(3)
        self.spread_claw()
        self.func("2", self.shengjiang, "1948")
        time.sleep(2)
        self.func("3", self.huatai, "1748")
        time.sleep(2)
        self.closed_claw()

    def spread_claw(self, v="250", v1="250", x=70):
        self.func("8", self.duoji, str(500-x), v)
        self.func("8", self.duoji1, str(500+x), v1)
        self.func("8", self.duoji, str(500-x), v)
        self.func("8", self.duoji1, str(500+x), v1)
        time.sleep(1)

    def closed_claw(self, v="300", v1="300"):
        self.func("8", self.duoji, "760", v)
        self.func("8", self.duoji1, "260", v1)
        self.func("8", self.duoji, "760", v)
        self.func("8", self.duoji1, "260", v1)
        time.sleep(1)

    def __spread_claw__(self, x=250, wait=False):
        self.func("4", self.duoji, str(2048+x))
        self.func("4", self.duoji1, str(2048-x))
        self.func("4", self.duoji, str(2048+x))
        self.func("4", self.duoji1, str(2048-x))

        time.sleep(1)

    def __closed_claw__(self, x=0):
        self.func("4", self.duoji1, "3048")
        self.func("4", self.duoji, "1148")
        self.func("4", self.duoji1, "3048")
        self.func("4", self.duoji, "1148")
        time.sleep(1)


def normalize_pos(pos):
    if pos < 6:
        return pos
    return (pos-6)
