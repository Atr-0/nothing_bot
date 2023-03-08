#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import math


def distance(v1, v2):
    v3 = v1-v2
    X = v3[0] * v3[0]
    Y = v3[1] * v3[1]
    # Z = v3[2] * v3[2]
    return math.sqrt(X + Y)


def lerp(_from, to, t, clamp=True):
    if clamp:
        if t >= 1:
            return to
        elif t <= 0:
            return _from
    return _from + (to - _from) * t


def normalize_angle(angle):
    res = angle
    while res > math.pi:
        res -= 2.0*math.pi
    while res < -math.pi:
        res += 2.0*math.pi
    return res


def euler_from_quaternion(x, y, z, w):
    """
    Convert a quaternion into euler angles (roll, pitch, yaw)
    roll is rotation around x in radians (counterclockwise)
    pitch is rotation around y in radians (counterclockwise)
    yaw is rotation around z in radians (counterclockwise)
    """
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = math.atan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch_y = math.asin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = math.atan2(t3, t4)

    return roll_x, pitch_y, yaw_z  # in radians
