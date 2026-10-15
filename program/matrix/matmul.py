#!/usr/bin/env python3
"""
matmul.py  --  Matrix Multiplication Race  (multiprocessing + curses)

Computes  C = A x B  where A and B are read from A.txt and B.txt.
The rows of C are cut into 8 jobs, and the jobs are shared out
among N worker processes.

Prepare:  python3 make_matrix.py       (creates A.txt and B.txt, 700 x 700)

Run:      python3 matmul.py            (1 process does all 8 jobs)
          python3 matmul.py 2          (2 processes, 4 jobs each)
          python3 matmul.py 4          (4 processes, 2 jobs each)
          python3 matmul.py 8          (8 processes, 1 job each)

The result is written to C.txt. The CHECKSUM (sum of all numbers in C)
must be the same for every number of processes!

Observe:  ps -ef | grep matmul    (in another terminal, during the race)

Windows users: pip install windows-curses
"""

import os
import sys
import time
import curses
import multiprocessing

JOBS = 20


def read_matrix(filename):
    """Read a matrix from a text file: one row per line."""
    matrix = []
    f = open(filename)
    for line in f:
        row = []
        for number in line.split():
            row.append(int(number))
        matrix.append(row)
    f.close()
    return matrix


def work(jobs, A, B, C, progress, pids):
    """Worker: compute the rows of C that belong to every job in 'jobs'.
    Write the rows into the shared array C, report progress and our PID."""
    n = len(A)
    for job in jobs:
        pids[job] = os.getpid()
        first = job * n // JOBS                # first row of this job
        last = (job + 1) * n // JOBS           # one past the last row
        for i in range(first, last):
            row = []
            for j in range(n):
                total = 0
                for k in range(n):
                    total = total + A[i][k] * B[k][j]
                row.append(total)
            C[i * n:(i + 1) * n] = row         # store row i in shared memory
            progress[job] = (i + 1 - first) * 100 // (last - first)


def main(screen, num_procs):
    curses.curs_set(0)

    # ---- read the input files ----
    screen.addstr(0, 0, "Reading A.txt and B.txt ...")
    screen.refresh()
    A = read_matrix("A.txt")
    B = read_matrix("B.txt")
    n = len(A)

    # Shared memory: every process has its own memory, so the workers
    # must write their results into a SHARED array.
    # C is stored as one long list: element (i, j) is at C[i * n + j].
    C = multiprocessing.Array("q", n * n, lock=False)
    progress = multiprocessing.Array("i", JOBS)
    pids = multiprocessing.Array("i", JOBS)

    # Share the jobs out:  process 0 gets jobs 0, N, 2N, ...
    #                      process 1 gets jobs 1, N+1, ...
    job_lists = []
    for w in range(num_procs):
        job_lists.append(list(range(w, JOBS, num_procs)))

    screen.erase()
    screen.addstr(0, 0, "MATRIX MULTIPLICATION RACE: C = A x B  (%d x %d)" % (n, n))
    screen.addstr(1, 0, "%d job(s), %d process(es).  Main program PID: %d"
                  % (JOBS, num_procs, os.getpid()))
    for w in range(num_procs):
        screen.addstr(3 + w, 0, "Process %d will do jobs %s"
                      % (w + 1, [j + 1 for j in job_lists[w]]))
    screen.addstr(4 + num_procs, 0, "Press any key to start...")
    screen.refresh()
    screen.getch()

    workers = []
    for jobs in job_lists:
        p = multiprocessing.Process(target=work, args=(jobs, A, B, C, progress, pids))
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
        screen.addstr(0, 0, "Processes: %d   Matrix: %d x %d   Time: %5.1f s"
                      % (num_procs, n, n, time.time() - start))
        for j in range(JOBS):
            first = j * n // JOBS
            last = (j + 1) * n // JOBS - 1
            bar = "#" * (progress[j] // 5)
            pid = str(pids[j]) if pids[j] else "-"
            screen.addstr(2 + j, 0, "Job %d  rows %4d-%-4d PID %-7s [%-20s] %3d%%"
                          % (j + 1, first, last, pid, bar, progress[j]))
        screen.refresh()

        if not running:
            break
        time.sleep(0.1)

    for p in workers:
        p.join()
    total_time = time.time() - start

    # ---- save the result ----
    f = open("C.txt", "w")
    for i in range(n):
        f.write(" ".join(str(x) for x in C[i * n:(i + 1) * n]) + "\n")
    f.close()

    screen.addstr(3 + JOBS, 0, "Finished: %d process(es) took %.1f seconds."
                  % (num_procs, total_time))
    screen.addstr(4 + JOBS, 0, "Result written to C.txt.   CHECKSUM: %d" % sum(C))
    screen.addstr(5 + JOBS, 0, "This computer has %d CPU core(s)." % os.cpu_count())
    screen.addstr(7 + JOBS, 0, "Try again with another number, e.g.:  python3 matmul.py 4")
    screen.addstr(9 + JOBS, 0, "Press any key to quit.")
    screen.refresh()
    screen.getch()


if __name__ == "__main__":
    # Number of processes from the command line (default 1).
    num_procs = 1
    if len(sys.argv) > 1:
        try:
            num_procs = int(sys.argv[1])
        except ValueError:
            print("Usage: python3 matmul.py [number of processes, 1-%d]" % JOBS)
            sys.exit(1)
    if num_procs < 1 or num_procs > JOBS:
        print("Number of processes must be between 1 and %d." % JOBS)
        sys.exit(1)
    if not (os.path.exists("A.txt") and os.path.exists("B.txt")):
        print("A.txt or B.txt not found. Run first:  python3 make_matrix.py")
        sys.exit(1)

    curses.wrapper(main, num_procs)
