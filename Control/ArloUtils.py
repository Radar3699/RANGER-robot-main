from __future__ import print_function
from __future__ import division

import serial
import argparse
import numpy as np
import time

# define angle conversion factor
def AngleConvert(angle):
  return (angle/360 * 372)

# define distance conversion factor
def DistConvert(dist):
  return dist * 301

# send a turn command to rover
def ArloTurn(ser,speed,degrees):
  turn_string = 'TURN ' + str(int(AngleConvert(degrees))) + ' ' + str(speed)
  print(turn_string)
  ser.write(bytes(turn_string))

# send a move command to rover
def ArloMove(ser,speed,distance):
  move_string = 'MOVE ' + str(int(DistConvert(distance))) + ' ' + str(int(DistConvert(distance))) + ' ' + str(speed)
  ser.write(bytes(move_string))

# send a go command to rover
def ArloGo(ser,speed):
  move_string = 'GOSPD ' + str(speed) + ' ' + str(speed)
  ser.write(bytes(move_string))

# send a stop command to rover
def ArloStop(ser):
  move_string = 'GOSPD ' + str(0) + ' ' + str(0)
  ser.write(bytes(move_string))

# indefinitely rotate righ
def ArloRightRotate(ser,speed):
  move_string = 'GOSPD ' + str(speed) + ' ' + str(-1*speed)
  ser.write(bytes(move_string))

# indefinitely rotate left
def ArloLeftRotate(ser,speed):
  move_string = 'GOSPD ' + str(-1*speed) + ' ' + str(speed)
  ser.write(bytes(move_string))

# return left turn message string
def LeftTurnString(n):
  # guard for correct range
  if n <= 9:
    n1 = n
    n2 = 0
  if n > 9:
    n1 = 9
    n2 = (9-n)*-1
  # make progress bar
  lst=np.array(['|','-','-','-','-','-','-','-','-','-','|','-','-','-','-','-','-','-','-','-','|','-','-','-','-','-','-','-','-','-','|','-','-','-','-','-','-','-','-','-','|'])
  lst[20-n1:20] = '<'
  lst[10-n2:10] = '<'
  return ''.join(lst)

# return right turn message string
def RightTurnString(n):
  # guard for correct range
  if n <= 9:
    n1 = n
    n2 = 0
  if n > 9:
    n1 = 9
    n2 = (9-n)*-1
  # make progress bar
  lst=np.array(['|','-','-','-','-','-','-','-','-','-','|','-','-','-','-','-','-','-','-','-','|','-','-','-','-','-','-','-','-','-','|','-','-','-','-','-','-','-','-','-','|'])
  lst[21:21+n1] = '>'
  lst[31:31+n2] = '>'
  return ''.join(lst)

# define COLOR object for control UI
class COLORS(object):
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
