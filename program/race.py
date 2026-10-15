#!/usr/bin/env python3
"""
race.py  --  Progress Bar Race  (multiprocessing + curses)

Eight jobs. Each job counts prime numbers (heavy CPU work).
The jobs are shared out among N worker processes.

Run:      python3 race.py          (1 process does all 8 jobs)
          python3 race.py 2        (2 processes, 4 jobs each)
          python3 race.py 4        (4 processes, 2 jobs each)
          python3 race.py 8        (8 processes, 1 job each)

Compare the bars, the PIDs, and the time.
Observe:  ps -ef | grep race      (in another terminal, during the race)

Windows users: pip install windows-curses
"""

import os
import sys
import time
import curses
import multiprocessing

JOBS = 8
LIMIT = 500_000          # how many numbers each job checks (bigger = slower)


def work(jobs, progress, pids):
    """Worker: do every job in the list 'jobs', one after another.
    Report progress (0..100) and our PID into the shared arrays."""
    for job in jobs:
        pids[job] = os.getpid()
        count = 0
        for n in range(2, LIMIT):
            prime = True
            for d in range(2, int(n ** 0.5) + 1):
                if n % d == 0:
                    prime = False
                    break
            if prime:
                count = count + 1
            if n % (LIMIT // 100) == 0:
                progress[job] = n * 100 // LIMIT
        progress[job] = 100


def main(screen, num_procs):
    curses.curs_set(0)

    # Shared memory: normal lists would NOT work, because every
    # process has its own copy of memory.
    progress = multiprocessing.Array("i", JOBS)
    pids = multiprocessing.Array("i", JOBS)

    # Share the jobs out:  process 0 gets jobs 0, N, 2N, ...
    #                      process 1 gets jobs 1, N+1, ...
    job_lists = []
    for w in range(num_procs):
        job_lists.append(list(range(w, JOBS, num_procs)))

    screen.addstr(0, 0, "PROGRESS BAR RACE: %d job(s), %d process(es)" % (JOBS, num_procs))
    screen.addstr(1, 0, "Main program PID: %d" % os.getpid())
    for w in range(num_procs):
        screen.addstr(3 + w, 0, "Process %d will do jobs %s"
                      % (w + 1, [j + 1 for j in job_lists[w]]))
    screen.addstr(4 + num_procs, 0, "Press any key to start...")
    screen.refresh()
    screen.getch()

    workers = []
    for jobs in job_lists:
        p = multiprocessing.Process(target=work, args=(jobs, progress, pids))
        workers.append(p)

    start = time.time()
    for p in workers:
        p.start()

    while True:
        running = False
        for p in workers:
            if p.is_alive():
                running = True

        screen.erase()
        screen.addstr(0, 0, "Processes: %d   Time: %5.1f s"
                      % (num_procs, time.time() - start))
        for j in range(JOBS):
            bar = "#" * (progress[j] // 5)
            pid = str(pids[j]) if pids[j] else "-"
            screen.addstr(2 + j, 0, "Job %d  PID %-7s [%-20s] %3d%%"
                          % (j + 1, pid, bar, progress[j]))
        screen.refresh()

        if not running:
            break
        time.sleep(0.1)

    for p in workers:
        p.join()
    total = time.time() - start

    screen.addstr(3 + JOBS, 0, "Finished: %d process(es) took %.1f seconds."
                  % (num_procs, total))
    screen.addstr(4 + JOBS, 0, "This computer has %d CPU core(s)." % os.cpu_count())
    screen.addstr(6 + JOBS, 0, "Try again with another number, e.g.:  python3 race.py 4")
    screen.addstr(8 + JOBS, 0, "Press any key to quit.")
    screen.refresh()
    screen.getch()


if __name__ == "__main__":
    # Number of processes from the command line (default 1).
    num_procs = 1
    if len(sys.argv) > 1:
        try:
            num_procs = int(sys.argv[1])
        except ValueError:
            print("Usage: python3 race.py [number of processes, 1-%d]" % JOBS)
            sys.exit(1)
    if num_procs < 1 or num_procs > JOBS:
        print("Number of processes must be between 1 and %d." % JOBS)
        sys.exit(1)

    curses.wrapper(main, num_procs)

