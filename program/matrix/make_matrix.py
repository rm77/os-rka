#!/usr/bin/env python3
"""
make_matrix.py  --  create the input files for matmul.py

  python3 make_matrix.py          creates A.txt and B.txt, 700 x 700
  python3 make_matrix.py 300      creates smaller files, 300 x 300 (faster)

File format: one matrix row per line, numbers separated by spaces.
The numbers are random digits 0..9 (always the same, because of the seed).
"""

import sys
import random

size = 300
if len(sys.argv) > 1:
    size = int(sys.argv[1])

random.seed(2026)                       # same files every time

for name in ("A.txt", "B.txt"):
    f = open(name, "w")
    for i in range(size):
        row = []
        for j in range(size):
            row.append(str(random.randint(0, 9)))
        f.write(" ".join(row) + "\n")
    f.close()
    print("Created", name, "(%d x %d)" % (size, size))
