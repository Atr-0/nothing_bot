#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tf2_ros import transform_listener , TypeException
import tf2_ros
import math
import rclpy.time
import rclpy
from rclpy.duration import Duration

def getRobotPos():
    tfBuffer = tf2_ros.Buffer()
    try:
        # while(1):
        t = tfBuffer.lookup_transform("map","base_link",rclpy.time.Time(),Duration(seconds=1.0))
        msg = {t.transform.translation.x,
        t.transform.translation.y,
        t.transform.translation.z,
        t.transform.rotation.x,
        t.transform.rotation.y,
        t.transform.rotation.z,
        t.transform.rotation.w
        }
        print(msg)
        return msg  
    except AttributeError as e:
        print("listen to tf failed")
        return 0

# def getRobotYaw():
#     try:
#         (pos,ori) = transform_listener.Buffer.lookup_transform("map","base_link",duration(0.0))
#         euler = euler_from_quaternion(ori[0],ori[1],ori[2],ori[3])
#         print(euler)
#         return euler[2]
#     except TypeException as e:
#         print("listen to tf failed")
#         return 0
def distance(v1,v2):
    v3=v1-v2
    X = v3[0] * v3[0]
    Y = v3[1] * v3[1]
    # Z = v3[2] * v3[2]
    return math.Sqrt(X + Y)
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
    
    return roll_x, pitch_y, yaw_z # in radians
