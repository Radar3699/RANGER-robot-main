import curses
import numpy as np

scr = curses.initscr()
curses.halfdelay(5)
curses.noecho()

while True:
    char = scr.getch()
    scr.clear()
    if char != curses.ERR:
        scr.addstr(0, 0, chr(char))
        print(char)
        print(type(char))

        # If char is anumber key
        if char > 47 and char < 58:
            arr = np.array([int(chr(char))])
            np.save("label.npy",arr)

        # If pressed space
        if char == 32:
            np.save("label.npy",np.array([]))

        # If presed r (refresh)
        if char == 114:
            np.save("label.npy",np.array([99]))

        # If pressed c (read object semantics and save)
        if char == 99:
            arr = np.load("labelobj.npy")
            np.save("label.npy",arr)

    else:
        scr.addstr(0, 0, "Waiting")
