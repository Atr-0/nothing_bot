from utils import *
import basicMove
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int32

correct_sorting = np.array(
    [0, 0, 1, 1, 2, 2,
     0, 0, 1, 1, 2, 2]
)
original_sorting = np.array(
    [0, 1, 1, 2, 2, 0,
     0, 2, 0, 1, 1, 2]
)


class a_zone_grab():

    def __init__(self, func):
        global correct_sorting, original_sorting
        self.func = func
        self.dec = {
            "0": self.redZone(),
            "1": self.greenZone(),
            "2": self.blueZone(),
        }
        while not (np.array_equal(correct_sorting, original_sorting)):
            self.digui()
            break

    def func(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def digui(self, zone_num=2, pre_pos=0):
        self.dec = {
            "0": self.redZone(),
            "1": self.greenZone(),
            "2": self.blueZone(),
        }
        global correct_sorting, original_sorting
        pos = pre_pos
        if zone_num >= 0 and pre_pos <= 5:
            for i in range(4):
                if self.dec[str(zone_num)][i] != zone_num:
                    if (pos % 2 == 0) and (i == 0 or i == 2):
                        basicMove.movement(
                            7, 0.2, 0.0, 0.38, yaxis=False)
                        pos += 1
                        time.sleep(1)
                    elif (pos % 2 != 0) and (i == 1 or i == 3):
                        basicMove.movement(
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
                    basicMove.simple_movement(0.0, -0.1, 0, 10)
                    time.sleep(0.5)

                    # grab
                    self.grab_above() if i < 2 else self.grab_below()
                    time.sleep(0.5)

                    time.sleep(1)

                    basicMove.movement(
                        6, 0.2*dir, 0.0, goal_dis-0.03, yaxis=False)
                    time.sleep(0.5)

                    basicMove.simple_movement(0, -0.1, 0, 10)
                    time.sleep(1)
                    basicMove.simple_movement(-0.1, 0.0, 0, 10)
                    time.sleep(0.5)

                    # push
                    self.push_above() if goal_zone_item_pos < 2 else self.push_below()

                    time.sleep(0.5)

                    #########################################################

                    basicMove.simple_movement(0.1, 0.0, 0, 13)
                    time.sleep(0.5)

                    # grab
                    self.grab_above() if goal_zone_item_pos < 2 else self.grab_below()
                    time.sleep(0.5)

                    basicMove.movement(
                        6, 0.2*-dir, 0.0, goal_dis, yaxis=False)
                    time.sleep(1)
                    basicMove.simple_movement(0, -0.1, 0, 10)
                    time.sleep(0.5)

                    # push
                    self.push_above() if i < 2 else self.push_below()
                    time.sleep(1)

                    time.sleep(0.5)

                    # print(goal_dis, item_pos, goal_item_pos)
                    # print("a" if i > 1 else "b", " to ",
                    #       "a" if goal_zone_item_pos > 1 else "b",)

                    original_sorting[item_pos + (6 if i > 1 else 0)] = zone_num
                    original_sorting[goal_item_pos +
                                     (6 if goal_zone_item_pos > 1 else 0)] = goal_zone
                    print(original_sorting)

                    return self.digui(zone_num, pos)
            dis = 0.4 if (pos % 2 != 0) else 0.8
            if pos < 5:
                basicMove.movement(
                    6, 0.2, 0.0, dis, yaxis=False)
            pos += (1 if (dis == 0.4) else 2)
            time.sleep(0.5)
            return self.digui(zone_num-1, pos)

    def redZone(self):
        global correct_sorting, original_sorting
        redZone = (original_sorting[0], original_sorting[1],
                   original_sorting[6], original_sorting[7])
        return redZone

    def greenZone(self):
        global correct_sorting, original_sorting
        greenZone = (original_sorting[2], original_sorting[3],
                     original_sorting[8], original_sorting[9])
        return greenZone

    def blueZone(self):
        global correct_sorting, original_sorting
        blueZone = (original_sorting[4], original_sorting[5],
                    original_sorting[10], original_sorting[11])
        return blueZone

    def grab_below(self):
        self.func("1", "1", "1000")
        time.sleep(15)
        self.func("8", "09", "500", "350")
        self.func("8", "01", "500", "350")
        time.sleep(2)
        self.func("1", "1", "0000")
        time.sleep(15)
        self.func("8", "09", "780", "350")
        self.func("8", "01", "240", "380")
        time.sleep(2)

    def grab_above(self):
        time.sleep(2)
        self.func("1", "1", "2690")
        time.sleep(20)
        self.func("8", "09", "500", "350")
        self.func("8", "01", "500", "350")
        time.sleep(2)
        self.func("1", "2", "0600")
        time.sleep(8)
        self.func("8", "09", "780", "350")
        self.func("8", "01", "240", "380")
        time.sleep(2)
        self.func("1", "1", "0000")
        time.sleep(18)

    def push_below(self):
        time.sleep(2)
        self.func("1", "1", "1000")
        time.sleep(15)
        self.func("8", "09", "500", "300")
        self.func("8", "01", "500", "300")
        time.sleep(5)
        self.func("8", "09", "780", "350")
        self.func("8", "01", "240", "350")
        time.sleep(2)
        self.func("1", "1", "0000")
        time.sleep(5)

    def push_above(self):
        time.sleep(2)
        self.func("1", "1", "2690")
        time.sleep(20)
        self.func("8", "09", "500", "300")
        self.func("8", "01", "500", "300")
        time.sleep(5)
        self.func("8", "09", "780", "350")
        self.func("8", "01", "240", "350")
        time.sleep(5)
        self.func("1", "1", "0000")
        time.sleep(18)
