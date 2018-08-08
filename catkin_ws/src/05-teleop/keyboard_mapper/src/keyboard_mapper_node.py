#!/usr/bin/env python
import rospy
import math

import sys
import select
import termios
import tty

from duckietown_msgs.msg import Twist2DStamped, BoolStamped

from __builtin__ import True
from easy_node.easy_node import EasyNode

banner = """
Reading from the keyboard  and Publishing to AckermannDriveStamped!
---------------------------
Moving around:
        w
   a    s    d
anything else : stop
CTRL-C to quit
"""

keyBindings = {
    'w': (0.4, 0),
    'd': (0, -8),
    'a': (0, 8),
    's': (-0.4, 0),
    'c': (0, 0),
}


def getKey():
    tty.setraw(sys.stdin.fileno())
    select.select([sys.stdin], [], [], 0)
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

if __name__ == "__main__":
    #if len(sys.argv) < 3:
    #    print("usage: keyboard_teleop.py arg1 arg2")

    settings = termios.tcgetattr(sys.stdin)
    pub = None

    try:

        rospy.init_node('keyop')
        pub = rospy.Publisher("~car_cmd", Twist2DStamped, queue_size=1)
    except Exception as e:
        print 'error',e

    x = 0
    th = 0
    status = 0

    try:
        while(1):
            key = getKey()
            print key
            if key in keyBindings.keys():
                x = keyBindings[key][0]
                th = keyBindings[key][1]
            else:
                x = 0
                th = 0
                if (key == '\x03'):
                    break
            # Configuration parameters
            v_gain = 1.0
            omega_gain = 1.0
            steer_angle_gain = 1.0
            simulated_vehicle_length = 0.18

            # Input data
            # Left stick V-axis. Up is positive
            cmd_vel = x
            cmd_steer = th

            # Do the computation
            v = cmd_vel * v_gain

            if 1:
                # Implements Bicycle Kinematics - Nonholonomic Kinematics
                # see: https://inst.eecs.berkeley.edu/~ee192/sp13/pdf/steer-control.pdf
                steering_angle = cmd_steer * steer_angle_gain
                omega = v / simulated_vehicle_length * math.tan(steering_angle)
            else:
                # Holonomic Kinematics for Normal Driving
                omega = cmd_steer * omega_gain

            # Create the message and publish
            car_cmd_msg = Twist2DStamped()
            car_cmd_msg.header.stamp = rospy.get_rostime() 
            car_cmd_msg.v = x
            car_cmd_msg.omega = th
            pub.publish(car_cmd_msg)

    except Exception as e:
        print 'error', e
