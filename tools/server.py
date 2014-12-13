#!/usr/bin/env python

import os
import sys
import serial
import time
import math
import argparse
import OSC
import errno

BAUD_RATE = 38400
SAMPLE_DELAY = .01

def connect_poi(poi, device):
    while True:
        try:
            print "Connecting to %s..." % device
            ser = serial.Serial(device, 
                                BAUD_RATE, 
                                bytesize=serial.EIGHTBITS, 
                                parity=serial.PARITY_NONE, 
                                stopbits=serial.STOPBITS_ONE,
                                timeout=1)
        except serial.serialutil.SerialException, e:
            print "Serial error: ", e
            sys.exit(-1)
        except OSError, e:
            if e.errno == errno.EBUSY:
                print "Poi %d is busy. Sleep 1 second." % poi
                time.sleep(1)
                continue
                
            print "OS error: ", e
            sys.exit(-1)

        break

    print "connected."

    ser.flushInput()
    ser.flushOutput()

    return ser

def send_osc(ip, port, index, key, value):
    msg = OSC.OSCMessage()
    msg.setAddress("/rpoi-%d/%s" % (index, key))
    msg.append(value)
    client.sendto(msg, (ip, port))

def process_line(poi, line, log):
    try:
        ts, yaw, pitch, roll = line.strip().split(",")
    except ValueError as e:
        return

    line  = ""

    theta = math.radians(float(roll))
    phi = math.radians(float(pitch))
    x = math.sin(theta) * math.cos(phi)
    y = math.sin(theta) * math.sin(phi)
    z = math.cos(theta)

    if args.test:
        print "%s,%d,%.3f,%.3f,%.3f" % (ts, poi, x, y, z)

    if args.log:
        log.write("%s,%d,%.3f,%.3f,%.3f\n" % (ts, poi, x, y, z))

    if not args.noxmit:
        send_osc(args.ip, args.port, poi, "x", x)
        send_osc(args.ip, args.port, poi, "y", y)
        send_osc(args.ip, args.port, poi, "z", z)
        send_osc(args.ip, args.port, poi, "ts", ts)

def replay(client, args, replay):
    count = 0
    while True:
        line = replay.readline()
        if not line:
            break
        
        try:
            ts, index, x, y, z = line.strip().split(",")
        except ValueError as e:
            return

        ts = int(ts)
        index = int(index)

        if args.test:
            print "%s,%d,%s,%s,%s" % (ts, index, x, y, z)

        if not args.noxmit:
            send_osc(args.ip, args.port, index, "x", x)
            send_osc(args.ip, args.port, index, "y", y)
            send_osc(args.ip, args.port, index, "z", z)
            send_osc(args.ip, args.port, index, "ts", ts)

        if count % 2 == 0:
            time.sleep(SAMPLE_DELAY)

        count += 1

def main_loop(poi1, poi2, client, args, log):
    line = ""
    line2 = ""
    while True:
        ch = poi1.read()
        if not ch:
            print "Timeout"
            continue

        if ch == '\n':
            process_line(0, line, log)
            line = ""
        else:
            line += ch

        if poi2:
            ch2 = poi2.read()
            if not ch:
                print "Timeout"
                continue
        else:
            ch2 = ""

        if ch2 == '\n':
            process_line(1, line2, log)
            line2 = ""
        else:
            line2 += ch2

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action='store_true',
                        default=False, help="Instead of broadcasting, print data to console")
    parser.add_argument("--log", 
                        default="", help="Log data to the specified file")
    parser.add_argument("--replay", 
                        default="", help="Replay a given log file")
    parser.add_argument("--ip",
                        default="127.0.0.1", help="The ip to broadcast to. Default: localhost")
    parser.add_argument("--port",
                        type=int, default=9000, help="The port to broadcast to. Default: 9000")
    parser.add_argument("--device",
                        default="", help="The first serial device to read poi data from. Required, unless --replay is used")
    parser.add_argument("--device2",
                        default="", help="The second serial device to read poi data from. Optional.")
    parser.add_argument("--noxmit", action='store_true',
                        default=False, help="Do not send data to pure data. (default: off)")
    args = parser.parse_args()

    if args.device == "" and not args.replay:
        print "Must specify --device or --replay"
        sys.exit(-1)

    if args.replay and args.log:
        print "Canont specify --replay and --log at the same time."
        sys.exit(-1)

    print "Listening from %s" % args.device
    print "Sending to %s:%d" % (args.ip, args.port)

    client = OSC.OSCClient()

    if args.log:
        try:
            log = open(args.log, "w")
        except OSError as e:
            print "Failed to open log file: ", e
            sys.exit(-1)
    else:
        log = None

    if args.replay:
        try:
            replay_file = open(args.replay, "r")
        except OSError as e:
            print "Failed to open replay file: ", e
            sys.exit(-1)
    else:
        replay = None

    try:
        if args.device:
            poi1 = connect_poi(1, args.device)
        else:
            poi1 = None
        if args.device2:
            poi2 = connect_poi(2, args.device2)
        else:
            poi2 = None

        if args.replay:
            replay(client, args, replay_file)
        else:
            main_loop(poi1, poi2, client, args, log)
    except KeyboardInterrupt:
        print "cleaning up..."
        poi1.close()
        if poi2:
            poi2.close()
        if log:
            log.close()
