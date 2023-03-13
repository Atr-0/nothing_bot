from utils import *
import basic
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int32


a_zone_item_list = [0, 2, 0, 2, 1, 2,
                    0, 1, 1, 1, 0, 2]


c_zone_item_list = [1, 2, 0, 0, 0, 1,
                    2, 2, 0, 1, 1, 2]

d_zone_item_list = [-1, 1, 0, 0, 3, -1,
                    -1, 2, 0, 0, -1, 4]


class grab():

    def __init__(self, func, duoji, duoji1, mode=None):
        '''抓取
        Parameters:
                mode - 抓取模式:\n 
                a | c \n
                spread | closed \n
                grab_below | graba_above \n
                push_below | push_above 
        Return:
                NONE
        '''
        global a_zone_item_list
        self.duoji = duoji
        self.duoji1 = duoji1
        self.func = func
        self.dec = {
            "0": (a_zone_item_list[0], a_zone_item_list[1],
                  a_zone_item_list[6], a_zone_item_list[7]),
            "1": (a_zone_item_list[2], a_zone_item_list[3],
                  a_zone_item_list[8], a_zone_item_list[9]),
            "2": (a_zone_item_list[4], a_zone_item_list[5],
                  a_zone_item_list[10], a_zone_item_list[11]),
        }
        if mode == "a":
            self.a_zone_grab()
        elif mode == "c":
            self.c_zone_grab()
        elif mode == "spread":
            self.spread_claw()
        elif mode == "closed":
            self.closed_claw()
        elif mode == "grab_below":
            self.grab_below()
        elif mode == "graba_above":
            self.grab_above()
        elif mode == "push_below":
            self.push_below()
        elif mode == "push_above":
            self.push_above()

    def func(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def a_zone_grab(self, zone_num=2, pre_pos=0):
        global a_zone_item_list
        self.dec = {
            "0": (a_zone_item_list[0], a_zone_item_list[1],
                  a_zone_item_list[6], a_zone_item_list[7]),
            "1": (a_zone_item_list[2], a_zone_item_list[3],
                  a_zone_item_list[8], a_zone_item_list[9]),
            "2": (a_zone_item_list[4], a_zone_item_list[5],
                  a_zone_item_list[10], a_zone_item_list[11]),
        }

        pos = pre_pos
        if zone_num >= 0 and pre_pos <= 5:
            for i in range(4):
                if self.dec[str(zone_num)][i] != zone_num:
                    if (pos % 2 == 0) and (i == 0 or i == 2):
                        basic.movement(
                            7, 0.2, 0.0, 0.38, yaxis=False)
                        pos += 1
                        time.sleep(1)
                    elif (pos % 2 != 0) and (i == 1 or i == 3):
                        basic.movement(
                            7, -0.2, 0.0, 0.38, yaxis=False)
                        pos -= 1
                        time.sleep(1)

                    goal = zone_num - self.dec[str(zone_num)][i]
                    goal_zone = self.dec[str(zone_num)][i]

                    dir = 1 if goal > 0 else -1
                    goal_zone_item_pos = 0

                    for j in range(4):
                        if self.dec[str(goal_zone)][j] == zone_num:
                            goal_zone_item_pos = j
                            break
                    item_pos = (zone_num*2) + (i if i <= 1 else (i-2))
                    goal_item_pos = (
                        goal_zone*2) + (goal_zone_item_pos if goal_zone_item_pos <= 1 else (goal_zone_item_pos-2))

                    goal_dis = abs(item_pos-goal_item_pos)*0.4
                    print(goal_dis)
                    basic.simple_movement(0.0, -0.1, 0, 10)
                    time.sleep(0.5)

                    # grab
                    self.grab_above(True) if i < 2 else self.grab_below(True)
                    time.sleep(0.5)
                    # basicMove.simple_movement(0.0, 0.1, 0, 7)

                    time.sleep(1)

                    basic.movement(
                        6, 0.2*dir, 0.0, goal_dis-0.03, yaxis=False)
                    time.sleep(0.5)

                    basic.simple_movement(0, -0.1, 0, 10)
                    time.sleep(1)
                    basic.simple_movement(-0.1, 0.0, 0, 10)
                    time.sleep(0.5)

                    # push
                    self.push_above() if goal_zone_item_pos < 2 else self.push_below()

                    time.sleep(0.5)

                    #########################################################

                    basic.simple_movement(0.1, 0.0, 0, 13)
                    time.sleep(0.5)

                    # grab
                    self.grab_above() if goal_zone_item_pos < 2 else self.grab_below()
                    # basicMove.simple_movement(0, 0.1, 0, 7)
                    time.sleep(0.5)

                    basic.movement(
                        6, 0.2*-dir, 0.0, goal_dis, yaxis=False)
                    time.sleep(1)
                    basic.simple_movement(0, -0.1, 0, 10)
                    time.sleep(0.5)

                    # push
                    self.push_above(True) if i < 2 else self.push_below(True)
                    time.sleep(1)
                    # basicMove.simple_movement(0, 0.1, 0, 7)

                    time.sleep(0.5)

                    # print(goal_dis, item_pos, goal_item_pos)
                    # print("a" if i > 1 else "b", " to ",
                    #       "a" if goal_zone_item_pos > 1 else "b",)

                    a_zone_item_list[item_pos + (6 if i > 1 else 0)] = zone_num
                    a_zone_item_list[goal_item_pos +
                                     (6 if goal_zone_item_pos > 1 else 0)] = goal_zone
                    print(a_zone_item_list)

                    return self.a_zone_grab(zone_num, pos)
            dis = 0.4 if (pos % 2 != 0) else 0.8
            if pos < 5:
                basic.movement(
                    6, 0.2, 0.0, dis, yaxis=False)
            pos += (1 if (dis == 0.4) else 2)
            time.sleep(0.5)
            return self.a_zone_grab(zone_num-1, pos)

    def c_zone_grab(self, pos=5):
        global c_zone_item_list
        grab_pos, push_pos = -1, -1
        range_value = range(5, -1, -1)
        if pos <= 3:
            range_value = range(0, 6)

        for i in range_value:
            if grab_pos != -1:
                break
            for j in range(2):
                if c_zone_item_list[i+(j*6)] == 2:
                    grab_pos = i+(j*6)
                    print("ggg", grab_pos)
                    break

        for i in range_value:
            if push_pos != -1:
                break
            for j in range(2):
                if c_zone_item_list[i+(j*6)] == 0:
                    push_pos = i+(j*6)
                    print("ppp", push_pos)
                    break
        if push_pos == -1 and grab_pos == -1:
            return
        norm_grab = normalize_pos(grab_pos)
        norm_push = normalize_pos(push_pos)
        to_grab_dis = (pos-norm_grab)
        to_push_dis = (norm_grab-norm_push)
        time.sleep(0.5)
        if to_grab_dis != 0:
            basic.movement(6, 0.3*(to_grab_dis/abs(to_grab_dis)),
                           0, 0.4*abs(to_grab_dis))
        c_zone_item_list[grab_pos] = 1
        ##### grab#####
        time.sleep(0.5)
        if to_push_dis != 0:
            basic.movement(6, 0.3*(to_push_dis/abs(to_push_dis)),
                           0, 0.4*abs(to_push_dis))
        ##### push#####
        c_zone_item_list[push_pos] = 1
        return self.c_zone_grab(normalize_pos(push_pos))

    def d_zone_grab(self, pos=6):
        wangzai, xuehua, wanglaoji, ADgai = 1, 2, 3, 4

        grab_pos, push_pos = -1, -1
        range_value = range(6, 0, -1)
        if pos <= 3:
            range_value = range(1, 7)

        for i in range_value:
            if grab_pos != -1:
                break
            for j in range(2):
                if c_zone_item_list[i+(j*5)] == 2:
                    grab_pos = i+(j*5)
                    print("ggg", grab_pos)
                    break

        for i in range_value:
            if push_pos != -1:
                break
            for j in range(2):
                if c_zone_item_list[i+(j*5)] == 0:
                    push_pos = i+(j*5)
                    print("ppp", push_pos)
                    break

    def grab_below(self):
        self.func("2", "02", "3048")
        time.sleep(4)

        self.func("3", "08", "2098")
        time.sleep(0.5)
        self.spread_claw()
        self.func("3", "08", "2148")
        time.sleep(1)
        self.closed_claw()
        time.sleep(2)
        self.func("3", "08", "1848")
        time.sleep(2)

    def grab_above(self):
        self.func("2", "02", "1508")
        time.sleep(4)

        self.func("3", "08", "2098")
        time.sleep(0.5)
        self.spread_claw()
        self.func("3", "08", "2148")
        time.sleep(1)
        self.closed_claw()
        time.sleep(2)
        self.func("3", "08", "1848")
        time.sleep(2)

    def push_below(self):
        self.func("2", "02", "2748")
        time.sleep(4)

        self.func("3", "08", "2198")
        self.spread_claw()
        time.sleep(1)
        self.func("3", "08", "1848")
        time.sleep(2)
        self.closed_claw()

    def push_above(self):
        self.func("2", "02", "1048")
        time.sleep(5)

        self.func("3", "08", "2198")
        self.spread_claw()
        time.sleep(1)
        self.func("3", "08", "1848")
        time.sleep(2)
        self.closed_claw()

    def spread_claw(self, v="350", v1="350"):
        self.func("8", self.duoji, "500", v)
        self.func("8", self.duoji1, "500", v1)
        time.sleep(1)

    def closed_claw(self, v="350", v1="350"):
        self.func("8", self.duoji, "780", v)
        self.func("8", self.duoji1, "240", v1)
        time.sleep(1)


def normalize_pos(pos):
    if pos < 6:
        return pos
    return (pos-6)
