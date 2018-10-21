from __future__ import print_function
from __future__ import division

import serial
import argparse
import numpy as np
import time
from ArloUtils import *
import curses
import culour

# add and parse args
parser = argparse.ArgumentParser(description='Connection string and speed for Rover')
parser.add_argument("--connect", type=str, default='/dev/ttyACM0', help='connection string for serial port')
parser.add_argument("--speed", type=int, default=800, help='speed for this instance in m/s')
parser.add_argument("--flip", default=False, help='whether direction of motion should be flipped')
args = parser.parse_args()
print('Connection string:',args.connect)
print('Speed:',args.speed)
print('Direction flip:', args.flip)

def command_filter(ch):
  global left_turn_counter
  global right_turn_counter

  if ch==113:
    if right_turn_counter > 0:
      right_turn_counter -= 1
    elif left_turn_counter < 18:
      left_turn_counter += 1
  if ch ==101:
    if left_turn_counter > 0:
      left_turn_counter -= 1
    elif right_turn_counter < 18:
      right_turn_counter += 1
  if ch ==45:
    args.speed -= 100
  if ch ==61:
    args.speed += 100
  if left_turn_counter > 0:
    return LeftTurnString(left_turn_counter) + " " + str(10*left_turn_counter)
  if right_turn_counter > 0:
    return RightTurnString(right_turn_counter) + " " +str(10*right_turn_counter)
  if ch == -1:
    return "|---------|---------|---------|---------|"
  if ch == 119: #w
    return "|---------|---------^---------|---------|"
  if ch == 115: #s
    return "|---------|---------v---------|---------|"
  else:
    return "|---------|---------|---------|---------|"

def input_char(message,last_cmd):
  ch = None
  try:

    # setup curses window
    win = curses.initscr()
    curses.start_color()
    curses.noecho()
    win.erase()
    culour.addstr(win,0, 0, message)
    win.timeout(500)
    ch = win.getch()
    curses.flushinp()

    # get the next print statement
    msg = command_filter(ch)
  except: raise
  finally:
    curses.endwin()
  return (str(ch),msg)

# connect to rover
print("connecting...")
ser = serial.Serial(args.connect,timeout=3)
print(ser.read())
time.sleep(1)

# control loop
left_turn_counter = 0
right_turn_counter = 0
cmd = "-1"
last_cmd = "-1"
msg = "|---------|---------|---------|---------|"

while True:
  print(cmd,msg)

  # get message and command without pressing enter, with time limit
  msg = "Speed: " + str(args.speed) + " " + msg
  (cmd,msg) = input_char(msg,last_cmd)

  if cmd == "32" and left_turn_counter != 0:
    ArloTurn(ser,args.speed,-10*left_turn_counter)
    msg = msg + "      turn " + str(10*left_turn_counter) + " left"
    left_turn_counter = 0
  elif cmd == "32" and right_turn_counter != 0:
    ArloTurn(ser,args.speed,10*right_turn_counter)
    msg = msg + "      turn " + str(10*right_turn_counter) + " right"
    right_turn_counter = 0
  elif cmd == "119" and last_cmd == "-1":
    ArloGo(ser,args.speed)
    msg = msg + "go forward"
  elif cmd == "-1" and last_cmd == "119":
    ArloStop(ser)
    msg = msg + " stop"
  elif cmd == "49":
    ArloMove(ser,args.speed,0.1)
    msg = msg + " Move 10 cm"
  elif cmd == "50":
    ArloMove(ser,args.speed,0.2)
    msg = msg + " Move 20 cm"
  elif cmd == "51":
    ArloMove(ser,args.speed,0.3)
    msg = msg + " Move 30 cm"
  elif cmd == "52":
    ArloMove(ser,args.speed,0.4)
    msg = msg + " Move 40 cm"
  elif cmd == "53":
    ArloMove(ser,args.speed,0.5)
    msg = msg + " Move 50 cm"
  elif cmd == "54":
    ArloMove(ser,args.speed,0.6)
    msg = msg + " Move 60 cm"
  elif cmd == "55":
    ArloMove(ser,args.speed,0.7)
    msg = msg + " Move 70 cm"
  elif cmd == "56":
    ArloMove(ser,args.speed,0.8)
    msg = msg + " Move 80 cm"
  elif cmd == "57":
    ArloMove(ser,args.speed,0.9)
    msg = msg + " Move 90 cm"
  elif cmd == "115":
    ArloTurn(ser,args.speed,180)
    msg = msg + " turn 180"
  elif cmd == "97":
    ArloTurn(ser,args.speed,-90)
    msg = msg + " turn 90 left"
  elif cmd == "100":
    ArloTurn(ser,args.speed,90)
    msg = msg + " turn 90 right"
  print("\n\n\n\n",last_cmd,cmd,"\n\n\n\n")

  msg = msg + "\n" + "\n" + "{red}Basic:{end}   {green}q,e{end} (set turn angle)  space (send turn command)\n".format(green=COLORS.GREEN,end=COLORS.END,red=COLORS.RED) \
+ "\n" \
+ "                           {green}w{end} (hold w to move forward)\n".format(green=COLORS.GREEN,end=COLORS.END,blue=COLORS.BLUE,red=COLORS.RED) \
+ "                          {yellow}___{end}\n".format(yellow=COLORS.YELLOW,end=COLORS.END) \
+ " (tap for 90 deg left) {green}a{end} {yellow}/   \{end} {green}d{end} (tap for 90 deg right)\n".format(end=COLORS.END,green=COLORS.GREEN,yellow=COLORS.YELLOW,bold=COLORS.BOLD,red=COLORS.RED) \
+ "                         {yellow}\___/{end}\n".format(yellow=COLORS.YELLOW,end=COLORS.END) \
+ "                           {green}s{end} (tap for 180 deg turn)\n".format(green=COLORS.GREEN,end=COLORS.END,blue=COLORS.BLUE,red=COLORS.RED) \
+ "\n" \
+ "{red}Crawl:{end}  {green}1,2,...,9{end} (move n*10 cm)\n".format(green=COLORS.GREEN,end=COLORS.END,blue=COLORS.BLUE,red=COLORS.RED) \
+ "\n" \
+ "{red}Speed Change:{end} {green}-{end} (decrease speed)   {green}={end} (increase speed)".format(red=COLORS.RED,blue=COLORS.BLUE,green=COLORS.GREEN,end=COLORS.END)

  last_cmd=cmd
"""
Basic:   q,e (set turn angle)  space (send turn command)

                           w (hold w to move forward)
                          ___
a (tap for 90 deg left)  /   \ d (tap for 90 deg right)
                         \___/
                           s (tap for 180 deg turn)

Crawl:  1,2,...,9 (move n*10 cm)

Speed Change: - (decrease speed)   = (increase speed)
"""
