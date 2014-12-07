#!/usr/bin/env python

import os
import sys
import serial
import time

COUNT           = 100
BAUD_RATE       = 38400
device = sys.argv[1]

try:
    ser = serial.Serial(device, 
                        BAUD_RATE, 
                        bytesize=serial.EIGHTBITS, 
                        parity=serial.PARITY_NONE, 
                        stopbits=serial.STOPBITS_ONE,
                        timeout=1)
except serial.serialutil.SerialException, e:
    print "Serial error: " % e
    sys.exit(-1)

ser.flushInput()
ser.flushOutput()

total = 0
for i in xrange(COUNT):
    t0 = time.time()
    ser.write("?")
    ch = ser.read(1)
    t1 = time.time()

    if not ch:
        print "timeout"
    if ch != "?":
        print "got wrong char"

    print "%.4f s" % (t1 - t0)
    total += t1 - t0

print "Closing serial port"
print "%.4f average" % (total / COUNT)
ser.close()
