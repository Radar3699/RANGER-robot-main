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

# connect to rover
print("connecting...")
ser = serial.Serial(args.connect,timeout=3)
print(ser.read())

# control loop
while True:
  x = None
  y = None
  while x == None or y == None:
    print("(x,y):")
    x, y = map(str, raw_input().split())
    try:
      x = float(x)
      y = float(y)
    except:
       print("usage: <float float>")
       x = None
       y = None
  print("moving to:",(x,y))

  # guard for divide by zero
  if x == 0:
    x = 0.0000001
  if y == 0:
    y = 0.0000001

  # get turn angle
  interior_angle = np.arctan(abs(y/x)) * 180/np.pi
  if x > 0 and y > 0:
    angle = 90-interior_angle # turn right
  if x > 0 and y < 0:
    angle = 90 + interior_angle # turn right
  if x < 0 and y > 0:
    angle = -1 * (90-interior_angle) # turn left
  if x < 0 and y < 0:
    angle = -1 * (90 + interior_angle) # turn left
  angle = AngleConvert(angle)

  # turn rover
  turn_string = 'TURN ' + str(int(angle)) + ' ' + str(args.speed)
  ser.write(bytes(turn_string))
  time.sleep(2)

  # get distance
  dist = np.linalg.norm([abs(x),abs(y)])
  dist = DistConvert(dist)

  # move rover
  dist_string = 'MOVE ' + str(int(dist)) + ' ' + str(int(dist)) + ' ' + str(args.speed)
  if bool(args.flip)==True:
    dist_string = 'MOVE ' + str(int(dist)*-1) + ' ' +str(int(dist)*-1) + ' ' + str(args.speed)
  ser.write(bytes(dist_string))




