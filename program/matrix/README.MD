
#### matmul.py  --  Matrix Multiplication Race  (multiprocessing + curses)

Computes  C = A x B  where A and B are read from A.txt and B.txt.
The rows of C are cut into 8 jobs, and the jobs are shared out
among N worker processes.

```

Prepare:  
	  python3 make_matrix.py       (creates A.txt and B.txt, 700 x 700)

Run:      python3 matmul.py            (1 process does all 8 jobs)
          python3 matmul.py 2          (2 processes, 4 jobs each)
          python3 matmul.py 4          (4 processes, 2 jobs each)
          python3 matmul.py 8          (8 processes, 1 job each)
```
The result is written to C.txt. The CHECKSUM (sum of all numbers in C)
must be the same for every number of processes!

```
Observe:  ps -ef | grep matmul    (in another terminal, during the race)
```
