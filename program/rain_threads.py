#!/usr/bin/env python3
"""
rain_threads.py  --  Work Rain with THREADS  (curses)

Every column of "Matrix rain" belongs to one worker THREAD.
Each time a worker finishes a chunk of heavy work (checking numbers
for primes), its column falls one step.

Run this file, then run rain_processes.py and compare:
  Which one pours, which one drips?  Which one did more steps?

Run:      python3 rain_threads.py
Observe:  ps -eLf | grep rain_threads   (in another terminal, while it rains)
          top -H                        (threads of one process)

"""

import os
import time
import random
import curses
import threading

WORKERS = 8              # number of worker threads (= rain columns)
CHUNK = 20_000           # numbers checked per chunk (one rain step)
SECONDS = 10             # how long it rains
TRAIL = 8                # length of each falling trail
CHARS = "0123456789ABCDEF@#$%&*+=<>?"


def work(col, counters, ids, running):
    """Worker thread: check numbers for primes, chunk after chunk.
    After every chunk, add 1 to our counter (= one rain step)."""
    ids[col] = threading.get_native_id()      # this thread's TID
    while running[0]:
        for n in range(2, CHUNK):
            for d in range(2, int(n ** 0.5) + 1):
                if n % d == 0:
                    break
        counters[col] = counters[col] + 1


def main(screen):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    green = curses.color_pair(1)
    white = curses.color_pair(2) | curses.A_BOLD

    height, width = screen.getmaxyx()
    rows = height - 4                         # rows available for rain

    # Threads live in ONE process, so they share memory:
    # plain Python lists are enough.
    counters = [0] * WORKERS
    ids = [0] * WORKERS
    running = [True]

    screen.addstr(0, 0, "WORK RAIN with %d THREADS" % WORKERS)
    screen.addstr(1, 0, "Program PID: %d" % os.getpid())
    screen.addstr(3, 0, "Press any key to start...")
    screen.refresh()
    screen.getch()

    workers = []
    for col in range(WORKERS):
        t = threading.Thread(target=work, args=(col, counters, ids, running))
        t.start()
        workers.append(t)

    screen.erase()
    drawn = [0] * WORKERS                     # steps already drawn per column
    start = time.time()

    while time.time() - start < SECONDS:
        for col in range(WORKERS):
            x = (col + 1) * width // (WORKERS + 1)
            while drawn[col] < counters[col]:
                drawn[col] = drawn[col] + 1
                head = 3 + drawn[col] % rows
                prev = 3 + (drawn[col] - 1) % rows
                tail = 3 + (drawn[col] - TRAIL) % rows
                screen.addstr(prev, x, random.choice(CHARS), green)
                screen.addstr(head, x, random.choice(CHARS), white)
                screen.addstr(tail, x, " ")
            screen.addstr(2, x - 3, "%7d" % ids[col])

        total = sum(counters)
        elapsed = time.time() - start
        screen.addstr(0, 0, "THREADS   steps: %6d   speed: %6.1f steps/s   time left: %2d s "
                      % (total, total / max(elapsed, 1.0), SECONDS - elapsed))
        screen.addstr(1, 0, "All threads are inside ONE process, PID %d. "
                            "Numbers below are TIDs." % os.getpid())
        screen.refresh()
        time.sleep(0.05)

    running[0] = False                        # tell every thread to stop
    for t in workers:
        t.join()
    total = sum(counters)

    # ---- result ----
    screen.erase()
    screen.addstr(0, 0, "RESULT: %d THREADS, %d seconds" % (WORKERS, SECONDS))
    screen.addstr(2, 0, "Total steps : %d" % total)
    screen.addstr(3, 0, "Speed       : %.1f steps/s" % (total / SECONDS))
    screen.addstr(4, 0, "CPU cores   : %d" % os.cpu_count())
    screen.addstr(6, 0, "Write down the total, then run rain_processes.py.")
    screen.addstr(8, 0, "Press any key to quit.")
    screen.refresh()
    screen.getch()


if __name__ == "__main__":
    curses.wrapper(main)

