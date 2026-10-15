#!/usr/bin/env python3
"""
rain_processes.py  --  Work Rain with PROCESSES  (curses)

Every column of "Matrix rain" belongs to one worker PROCESS.
Each time a worker finishes a chunk of heavy work (checking numbers
for primes), its column falls one step.

Run rain_threads.py first, then this file, and compare:
  Which one pours, which one drips?  Which one did more steps?

Run:      python3 rain_processes.py
Observe:  ps -ef | grep rain_processes  (in another terminal, while it rains)
          top                           (press 1 to see every CPU core)

"""

import os
import time
import random
import curses
import multiprocessing

WORKERS = 8              # number of worker processes (= rain columns)
CHUNK = 20_000           # numbers checked per chunk (one rain step)
SECONDS = 10             # how long it rains
TRAIL = 8                # length of each falling trail
CHARS = "0123456789ABCDEF@#$%&*+=<>?"


def work(col, counters, ids, running):
    """Worker process: check numbers for primes, chunk after chunk.
    After every chunk, add 1 to our counter (= one rain step)."""
    ids[col] = os.getpid()                    # this process's PID
    while running.value:
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

    # Every process has its OWN memory, so plain lists would not work.
    # multiprocessing.Array / Value are SHARED memory between processes.
    counters = multiprocessing.Array("i", WORKERS)
    ids = multiprocessing.Array("i", WORKERS)
    running = multiprocessing.Value("i", 1)

    screen.addstr(0, 0, "WORK RAIN with %d PROCESSES" % WORKERS)
    screen.addstr(1, 0, "Main program PID: %d" % os.getpid())
    screen.addstr(3, 0, "Press any key to start...")
    screen.refresh()
    screen.getch()

    workers = []
    for col in range(WORKERS):
        p = multiprocessing.Process(target=work, args=(col, counters, ids, running))
        p.start()
        workers.append(p)

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
        screen.addstr(0, 0, "PROCESSES steps: %6d   speed: %6.1f steps/s   time left: %2d s "
                      % (total, total / max(elapsed, 1.0), SECONDS - elapsed))
        screen.addstr(1, 0, "Main PID %d. Each worker is its own process. "
                            "Numbers below are PIDs." % os.getpid())
        screen.refresh()
        time.sleep(0.05)

    running.value = 0                         # tell every process to stop
    for p in workers:
        p.join()
    total = sum(counters)

    # ---- result ----
    screen.erase()
    screen.addstr(0, 0, "RESULT: %d PROCESSES, %d seconds" % (WORKERS, SECONDS))
    screen.addstr(2, 0, "Total steps : %d" % total)
    screen.addstr(3, 0, "Speed       : %.1f steps/s" % (total / SECONDS))
    screen.addstr(4, 0, "CPU cores   : %d" % os.cpu_count())
    screen.addstr(6, 0, "Compare with the total from rain_threads.py.")
    screen.addstr(7, 0, "Why the difference? (hint: Python's GIL)")
    screen.addstr(9, 0, "Press any key to quit.")
    screen.refresh()
    screen.getch()


if __name__ == "__main__":
    curses.wrapper(main)

