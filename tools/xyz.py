#!/usr/bin/env python

import os
import sys
import math

r = 80

for i, line in enumerate(sys.stdin.readlines()):
    yaw, pitch, roll = line.strip().split(",")
    theta = math.radians(float(roll))
    phi = math.radians(float(pitch))
    x = r * math.sin(theta) * math.cos(phi)
    y = r * math.sin(theta) * math.sin(phi)
    z = r * math.cos(theta)
    print "%d,%s,%s,%.3f,%.3f,%.3f" % (i, pitch, roll, x, y, z)
