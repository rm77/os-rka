#!/usr/bin/env python3
"""
stars.py  --  three processes, three moving '*'

Each line is moved by its own process. Press q to quit.
"""

import os
import time
import signal
import curses
import multiprocessing


def worker(line, pos, width, delay, parent):
    signal.signal(signal.SIGTERM, signal.SIG_DFL)   # do not reset the terminal
    signal.signal(signal.SIGINT, signal.SIG_IGN)    # Ctrl+C is for the parent
    x = 0
    step = 1
    while os.getppid() == parent:             # stop if the parent is gone
        x = x + step
        if x >= width - 1 or x <= 0:
            step = -step
        pos[line] = x
        time.sleep(delay)


def main(screen):
    curses.curs_set(0)
    screen.nodelay(True)
    height, width = screen.getmaxyx()
    track = min(width - 14, 60)

    pos = multiprocessing.Array("i", 3)
    workers = []
    for line, delay in enumerate((0.03, 0.05, 0.08)):
        p = multiprocessing.Process(target=worker,
                                    args=(line, pos, track, delay, os.getpid()),
                                    daemon=True)
        p.start()
        workers.append(p)

    try:
        while screen.getch() not in (ord("q"), ord("Q")):
            screen.erase()
            for line in range(3):
                screen.addstr(1 + line * 2, 0, "%7d |%s|" % (workers[line].pid, " " * track))
                screen.addstr(1 + line * 2, 9 + pos[line], "*")
            screen.refresh()
            time.sleep(0.03)
    except KeyboardInterrupt:
        pass

    for p in workers:
        p.terminate()
        p.join()


if __name__ == "__main__":
    curses.wrapper(main)

