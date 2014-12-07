#!/usr/bin/env python

import os
import sys

for i, line in enumerate(sys.stdin.readlines()):
    yaw, pitch, roll = line.strip().split(",")
    print "%d,%s,%s,%s" % (i, yaw, pitch, roll)
