#!/usr/bin/env python

import os
import sys
import serial
import time
import math
import argparse
import OSC

BAUD_RATE = 38400

def send_osc(ip, port, index, key, value):
    msg = OSC.OSCMessage()
    msg.setAddress("/rpoi-%d/%s" % (index, key))
    msg.append(value)
    client.sendto(msg, (ip, port))

def main_loop(ser, client, args):
    line = ""
    while True:
        ch = ser.read()
        if not ch:
            print "Timeout"
            continue

        if ch != '\n':
            line += ch
            continue

        try:
            ts, yaw, pitch, roll = line.strip().split(",")
        except ValueError as e:
            continue

        line  = ""

        theta = math.radians(float(roll))
        phi = math.radians(float(pitch))
        x = math.sin(theta) * math.cos(phi)
        y = math.sin(theta) * math.sin(phi)
        z = math.cos(theta)

        if args.test:
            print "%s,%.3f,%.3f,%.3f" % (ts, x, y, z)
        else:
            send_osc(args.ip, args.port, 0, "x", x)
            send_osc(args.ip, args.port, 0, "y", y)
            send_osc(args.ip, args.port, 0, "z", z)
            send_osc(args.ip, args.port, 0, "ts", ts)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action='store_true',
                        default=False, help="Instead of broadcasting, print data to console")
    parser.add_argument("--ip",
                        default="127.0.0.1", help="The ip to broadcast to")
    parser.add_argument("--port",
                        type=int, default=9000, help="The port to broadcast to")
    parser.add_argument("--device",
                        default="", help="The serial device to read poi data from")
    args = parser.parse_args()

    if args.device == "":
        print "Must specify --device"
        sys.exit(-1)

    print "Listening from %s" % args.device
    print "Sending to %s:%d" % (args.ip, args.port)

    client = OSC.OSCClient()

    try:
        print "Connecting to Poi..."
        ser = serial.Serial(args.device, 
                            BAUD_RATE, 
                            bytesize=serial.EIGHTBITS, 
                            parity=serial.PARITY_NONE, 
                            stopbits=serial.STOPBITS_ONE,
                            timeout=1)
    except serial.serialutil.SerialException, e:
        print "Serial error: ", e
        sys.exit(-1)
    except OSError, e:
        print "OS error: ", e
        sys.exit(-1)

    print "connected."

    ser.flushInput()
    ser.flushOutput()

    try:
        main_loop(ser, client, args)
    except KeyboardInterrupt:
        print "cleaning up..."
        ser.close(ser)
