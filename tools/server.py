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
AV_SCALE_FACTOR = 100

client = OSC.OSCClient()

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
                print "Poi %d is busy. Sleep 3 seconds." % poi
                time.sleep(3)
                continue
                
            print "OS error: ", e
            sys.exit(-1)

        break

    print "connected."

    ser.flushInput()
    ser.flushOutput()

    return ser

def send_osc(ip, port, index, x, y, z, ts, av):
    msg = OSC.OSCMessage()
    msg.setAddress("/rpoi-%d" % index)
    msg.append(x)
    msg.append(y)
    msg.append(z)
    msg.append(ts)
    msg.append(av)
    client.sendto(msg, (ip, port))

def dotproduct(v1, v2):
    return sum((a*b) for a, b in zip(v1, v2))

def length(v):
    return math.sqrt(dotproduct(v, v))

def angle_between_vectors(v1, v2):
    dp = dotproduct(v1, v2)
    if dp > 1.0:
        dp = 1.0
    if dp < -1.0:
        dp = -1.0
    return math.acos(dp)

def process_line(poi, line, log, last_v, last_t):
    try:
        ts, yaw, pitch, roll = line.strip().split(",")
    except ValueError as e:
        return ((0,0,0), 0)

    line  = ""

    theta = math.radians(float(roll))
    phi = math.radians(float(pitch))
    x = math.sin(theta) * math.cos(phi)
    y = math.sin(theta) * math.sin(phi)
    z = math.cos(theta)
    ts = int(ts)

    av = angle_between_vectors((y, z), last_v) * AV_SCALE_FACTOR 
    if args.test:
        print "%d,%d,%.4f,%.4f,%.4f,%.4f" % (ts, poi, x, y, z, av)

    if args.log:
        log.write("%d,%d,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f\n" % (ts, poi, x, y, z, av, float(yaw), float(pitch), float(roll)))

    if not args.noxmit:
        send_osc(args.ip, args.port, poi, x, y, z, ts, av)

    return ((y, z), ts)

def replay(args, replay):
    count = 0
    while True:
        line = replay.readline()
        if not line:
            print "Reached end of file, starting over again"
            replay.seek(0)
            continue
        
        try:
            ts, index, x, y, z, av = line.strip().split(",")
        except ValueError as e:
            try:
                ts, index, x, y, z = line.strip().split(",")
                av = "0"
            except ValueError as e:
                return

        ts = int(ts)
        index = int(index)
        x = float(x)
        y = float(y)
        z = float(z)
        av = float(av)

        if args.test:
            print "%d,%d,%.3f,%.3f,%.3f,%.4f" % (ts, index, x, y, z, av)

        if not args.noxmit:
            send_osc(args.ip, args.port, index, x, y, z, ts, av)

        if count % 2 == 0:
            time.sleep(SAMPLE_DELAY)

        count += 1

def main_loop(poi1, poi2, args, log):
    line = ""
    line2 = ""
    last_0_vector = [0, 0, 1]
    last_1_vector = [0, 0, 1]
    last_0_ts = 0
    last_1_ts = 0
    while True:
        ch = poi1.read()
        if not ch:
            print "Timeout"
            continue

        if ch == '\n':
            last_0_vector, last_0_ts = process_line(0, line, log, last_0_vector, last_0_ts)
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
            last_1_vector, last_1_ts = process_line(1, line2, log, last_1_vector, last_1_ts)
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
                        type=int, default=9000, help="The port to broadcast poi 1 to. Default: 9000")
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
            replay(args, replay_file)
        else:
            main_loop(poi1, poi2, args, log)
    except KeyboardInterrupt:
        print "cleaning up..."
        if poi1:
            poi1.close()
        if poi2:
            poi2.close()
        if log:
            log.close()
