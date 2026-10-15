#!/usr/bin/env python3
"""
tetris.py  --  a simple Tetris, with gravity in its own process

    main process     reads the keys, moves the piece, draws the screen
    gravity process  ticks a shared counter: every tick = one row down

Keys:  left/right or a/d = move    up or w = rotate    down or s = drop one
       space = drop all the way    q = quit

Try:   kill -STOP <gravity PID>   ... and the pieces stop falling
       kill -CONT <gravity PID>   ... and they fall again
"""

import os
import time
import random
import signal
import curses
import multiprocessing

WIDTH = 10
HEIGHT = 20

# each piece: 4 cells (row, column) around the center (0, 0)
SHAPES = [
    [(0, -1), (0, 0), (0, 1), (0, 2)],     # I
    [(0, 0), (0, 1), (1, 0), (1, 1)],      # O
    [(0, -1), (0, 0), (0, 1), (1, 0)],     # T
    [(0, 0), (0, 1), (1, -1), (1, 0)],     # S
    [(0, -1), (0, 0), (1, 0), (1, 1)],     # Z
    [(0, -1), (0, 0), (0, 1), (1, 1)],     # J
    [(0, -1), (0, 0), (0, 1), (1, -1)],    # L
]


def gravity(ticks, delay, parent):
    """Gravity process: add 1 to the shared counter every 'delay' seconds."""
    signal.signal(signal.SIGTERM, signal.SIG_DFL)   # do not reset the terminal
    signal.signal(signal.SIGINT, signal.SIG_IGN)    # Ctrl+C is for the parent
    while os.getppid() == parent:                   # stop if the game is gone
        time.sleep(delay.value)
        ticks.value = ticks.value + 1


def fits(board, cells, row, col):
    """True if the piece 'cells' placed at (row, col) is inside and free."""
    for r, c in cells:
        y = row + r
        x = col + c
        if x < 0 or x >= WIDTH or y >= HEIGHT:
            return False
        if y >= 0 and board[y][x]:
            return False
    return True


def main(screen):
    curses.curs_set(0)
    screen.nodelay(True)
    screen.keypad(True)
    height, width = screen.getmaxyx()
    if height < HEIGHT + 3 or width < 2 * WIDTH + 34:
        screen.nodelay(False)
        screen.addstr(0, 0, "Terminal too small: need %d x %d. Press a key."
                      % (2 * WIDTH + 34, HEIGHT + 3))
        screen.getch()
        return
    if curses.has_colors():
        curses.start_color()
        for i, color in enumerate((curses.COLOR_CYAN, curses.COLOR_YELLOW,
                                   curses.COLOR_MAGENTA, curses.COLOR_GREEN,
                                   curses.COLOR_RED, curses.COLOR_BLUE,
                                   curses.COLOR_WHITE)):
            curses.init_pair(i + 1, color, curses.COLOR_BLACK)

    # ---- start the gravity process ----
    ticks = multiprocessing.Value("i", 0)           # shared with gravity
    delay = multiprocessing.Value("d", 0.5)         # seconds per row
    worker = multiprocessing.Process(target=gravity,
                                     args=(ticks, delay, os.getpid()),
                                     daemon=True)
    worker.start()

    board = [[0] * WIDTH for _ in range(HEIGHT)]    # 0 = empty, 1..7 = color
    kind = random.randrange(7)
    nxt = random.randrange(7)
    cells = SHAPES[kind]
    row, col = 0, WIDTH // 2 - 1
    last_tick = 0
    score = 0
    lines = 0
    over = False

    try:
        while True:
            key = screen.getch()
            if key in (ord("q"), ord("Q")):
                break

            if not over:
                # ---- keys ----
                if key in (curses.KEY_LEFT, ord("a")) and fits(board, cells, row, col - 1):
                    col = col - 1
                if key in (curses.KEY_RIGHT, ord("d")) and fits(board, cells, row, col + 1):
                    col = col + 1
                if key in (curses.KEY_UP, ord("w")) and kind != 1:      # O does not turn
                    turned = [(c, -r) for r, c in cells]
                    if fits(board, turned, row, col):
                        cells = turned
                if key in (curses.KEY_DOWN, ord("s")) and fits(board, cells, row + 1, col):
                    row = row + 1
                drop = False
                if key == ord(" "):
                    while fits(board, cells, row + 1, col):
                        row = row + 1
                    drop = True

                # ---- gravity: one row down for every new tick ----
                if ticks.value != last_tick or drop:
                    last_tick = ticks.value
                    if fits(board, cells, row + 1, col):
                        row = row + 1
                    else:
                        # the piece lands: copy it into the board
                        for r, c in cells:
                            if row + r >= 0:
                                board[row + r][col + c] = kind + 1
                        # remove full rows
                        full = [y for y in range(HEIGHT) if all(board[y])]
                        for y in full:
                            del board[y]
                            board.insert(0, [0] * WIDTH)
                        lines = lines + len(full)
                        score = score + [0, 100, 300, 500, 800][len(full)]
                        delay.value = max(0.1, 0.5 - (lines // 5) * 0.04)
                        # the next piece
                        kind = nxt
                        nxt = random.randrange(7)
                        cells = SHAPES[kind]
                        row, col = 0, WIDTH // 2 - 1
                        if not fits(board, cells, row, col):
                            over = True

            # ---- draw ----
            screen.erase()
            for y in range(HEIGHT):
                screen.addstr(1 + y, 0, "|")
                for x in range(WIDTH):
                    if board[y][x]:
                        screen.addstr(1 + y, 1 + 2 * x, "[]", curses.color_pair(board[y][x]))
                    else:
                        screen.addstr(1 + y, 1 + 2 * x, " .")
                screen.addstr(1 + y, 1 + 2 * WIDTH, "|")
            screen.addstr(1 + HEIGHT, 0, "+" + "-" * (2 * WIDTH) + "+")
            if not over:
                for r, c in cells:
                    if row + r >= 0:
                        screen.addstr(1 + row + r, 1 + 2 * (col + c), "[]",
                                      curses.color_pair(kind + 1) | curses.A_BOLD)

            px = 2 * WIDTH + 5
            screen.addstr(1, px, "Score  %d" % score)
            screen.addstr(2, px, "Lines  %d" % lines)
            screen.addstr(4, px, "Next")
            for r, c in SHAPES[nxt]:
                screen.addstr(6 + r, px + 4 + 2 * c, "[]", curses.color_pair(nxt + 1))
            screen.addstr(10, px, "Game PID     %d" % os.getpid())
            screen.addstr(11, px, "Gravity PID  %d" % worker.pid)
            screen.addstr(12, px, "Ticks        %d" % ticks.value)
            screen.addstr(13, px, "Delay        %.2f s" % delay.value)
            screen.addstr(15, px, "a d  move    w  rotate")
            screen.addstr(16, px, "s    down    space  drop")
            screen.addstr(17, px, "q    quit")
            if over:
                screen.addstr(9, 3, " GAME OVER ", curses.A_REVERSE)
            screen.refresh()
            time.sleep(0.02)
    except KeyboardInterrupt:
        pass

    worker.terminate()
    worker.join()


if __name__ == "__main__":
    curses.wrapper(main)

