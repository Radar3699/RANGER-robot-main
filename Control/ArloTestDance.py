from __future__ import print_function
from __future__ import division

import serial
import argparse
import numpy as np
import time
from ArloUtils import *

# add and parse args
parser = argparse.ArgumentParser(description='Connection string and speed for Rover')
parser.add_argument("--connect", type=str, default='/dev/ttyACM0', help='connection string for serial port')
parser.add_argument("--speed", type=int, default=800, help='speed for this instance in m/s')
parser.add_argument("--flip", default=False, help='whether direction of motion should be flipped')
args = parser.parse_args()
print('Connection string:',args.connect)
print('Speed:',args.speed)
print('Direction flip:', args.flip)
sleep_time = 5

# test connection
print("-----TESTING-----")
print("TEST: Connection")
ser = serial.Serial(args.connect,timeout=3)
string = ser.read()
if string != '':
    print("Passed")
if string == '':
    print("Failed")

# test movement
print("TEST: Movement")
print("A")
ArloMove(ser,args.speed,1)
time.sleep(sleep_time)
print("B")
ArloTurn(ser,args.speed,90)
time.sleep(sleep_time)
print("C")
ArloMove(ser,args.speed,1.5)
time.sleep(sleep_time)
print("D")
ArloTurn(ser,args.speed,135)
time.sleep(sleep_time)
print("E")
ArloMove(ser,args.speed,1.803)
time.sleep(sleep_time)
print("F")
ArloTurn(ser,args.speed,180)
time.sleep(sleep_time)
print("G")
ArloMove(ser,args.speed,1.803)
time.sleep(sleep_time)
print("H")
ArloTurn(ser,args.speed,135)
time.sleep(sleep_time)
print("I")
ArloMove(ser,args.speed,1)
time.sleep(sleep_time)
print("J")
ArloTurn(ser,args.speed,90)
time.sleep(sleep_time)
print("K")
ArloMove(ser,args.speed,1.5)
time.sleep(sleep_time)
print("L")
ArloTurn(ser,args.speed,450)
print("Finished")
