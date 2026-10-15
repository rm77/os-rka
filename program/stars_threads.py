#!/usr/bin/env python3
"""
stars_threads.py  --  three threads, three moving '*'

Each line is moved by its own thread. Press q to quit.
"""

import time
import curses
import threading


def worker(line, pos, tids, width, delay, running):
    tids[line] = threading.get_native_id()
    x = 0
    step = 1
    while running[0]:
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

    pos = [0, 0, 0]
    tids = [0, 0, 0]
    running = [True]
    workers = []
    for line, delay in enumerate((0.03, 0.05, 0.08)):
        t = threading.Thread(target=worker,
                             args=(line, pos, tids, track, delay, running),
                             daemon=True)
        t.start()
        workers.append(t)

    try:
        while screen.getch() not in (ord("q"), ord("Q")):
            screen.erase()
            for line in range(3):
                screen.addstr(1 + line * 2, 0, "%7d |%s|" % (tids[line], " " * track))
                screen.addstr(1 + line * 2, 9 + pos[line], "*")
            screen.refresh()
            time.sleep(0.03)
    except KeyboardInterrupt:
        pass

    running[0] = False
    for t in workers:
        t.join()


if __name__ == "__main__":
    curses.wrapper(main)
