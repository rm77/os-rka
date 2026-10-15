#!/usr/bin/env python3
"""
pcbview.py  --  watch the PCB and TCBs of a running program  (curses)

The Linux kernel keeps a Process Control Block (PCB) for every process
and a Thread Control Block (TCB) for every thread (both are a
"task_struct" inside the kernel). We cannot read kernel memory directly,
but the kernel shows us most of the fields in the /proc file system:

    /proc/<PID>/status, stat, fd/, maps    -> the PCB
    /proc/<PID>/task/<TID>/...              -> one TCB per thread

How to use (two terminals):

    Terminal 1:  python3 pcbview.py matmul      (start the viewer first)
    Terminal 2:  python3 matmul.py 4            (then start the program)

The word can be any part of the command: race, rain, matmul, ...
or a PID number:  python3 pcbview.py 1234

Two views:
    ALL view    (start)  every process with its threads, one line each
    DETAIL view          the full PCB and TCB table of one process

Keys:  n / p   (or arrow keys)  select next / previous process
       d       DETAIL view of the selected process
       a       back to the ALL view
       q       quit
"""

import os
import sys
import time
import curses

TICKS = os.sysconf("SC_CLK_TCK")            # clock ticks per second
POLICY = {0: "NORMAL", 1: "FIFO", 2: "RR", 3: "BATCH", 5: "IDLE", 6: "DEADLINE"}


def read_text(path):
    """Return the content of a /proc file, or "" if it is gone."""
    try:
        f = open(path)
        text = f.read()
        f.close()
        return text
    except OSError:
        return ""


def read_status(path):
    """/proc/.../status  ->  dictionary  {"State": "R (running)", ...}"""
    info = {}
    for line in read_text(path + "/status").splitlines():
        key, _, value = line.partition(":")
        info[key] = value.strip()
    return info


def read_stat(path):
    """/proc/.../stat  ->  list of fields.  field[N] = field number N
    from 'man proc'  (field[3] = state, field[14] = utime, ...)"""
    text = read_text(path + "/stat")
    if not text:
        return []
    end = text.rfind(")")                   # the name may contain spaces
    return ["", text[:text.find(" ")], text[text.find("(") + 1:end]] \
        + text[end + 2:].split()


def cpu_percent(previous, key, ticks, now):
    """CPU% used since the last screen update (100% = one full core)."""
    busy = 0.0
    if key in previous:
        old_ticks, old_time = previous[key]
        busy = (ticks - old_ticks) / TICKS / max(now - old_time, 0.1) * 100
    previous[key] = (ticks, now)
    return busy


def find_pids(word):
    """Return (matching PIDs, {pid: name} of every process, {pid: [children]})."""
    found = []
    names = {}
    children = {}
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        pid = int(entry)
        stat = read_stat("/proc/" + entry)
        if not stat:
            continue
        names[pid] = stat[2]
        ppid = int(stat[4])
        children.setdefault(ppid, []).append(pid)
        if pid == os.getpid():
            continue                        # do not watch ourselves
        if word.isdigit():
            if pid == int(word):
                found.append(pid)
        else:
            cmd = read_text("/proc/%d/cmdline" % pid).replace("\0", " ")
            if word in cmd and "pcbview" not in cmd:
                found.append(pid)
    found.sort()
    return found, names, children


def main(screen, word):
    curses.curs_set(0)
    screen.timeout(1000)                    # refresh every second
    choice = 0
    view = "all"                            # "all" or "detail"
    previous = {}                           # tid -> (cpu ticks, time)

    while True:
        height, width = screen.getmaxyx()
        lines = []                          # everything to draw this round
        pids, names, children = find_pids(word)
        now = time.time()

        if not pids:
            lines.append("PCB / TCB VIEWER   waiting for a process matching '%s' ..." % word)
            lines.append("")
            lines.append("Start your program in another terminal, e.g.  python3 %s.py" % word)
            lines.append("Press q to quit.")
        elif view == "all":
            choice = choice % len(pids)
            lines.append("ALL PROCESSES matching '%s'   [n]/[p] select  [d]etail  [q]uit"
                         % word)
            lines.append("Process line = PCB, indented lines = TCBs (when THR > 1), "
                         "* = main thread")
            lines.append("")
            lines.append("%-14s %-6s %-5s %-3s %5s %7s %7s %4s %9s %8s"
                         % ("PID / TID", "PPID", "STATE", "CPU", "CPU%", "USER s",
                            "SYS s", "THR", "RSS", "SWITCHES"))
            total_cpu = 0.0
            total_threads = 0
            select_row = 0
            for pid in pids:
                path = "/proc/%d" % pid
                sf = read_stat(path)
                st = read_status(path)
                if not sf:
                    continue
                busy = cpu_percent(previous, "p%d" % pid,
                                   int(sf[14]) + int(sf[15]), now)
                total_cpu = total_cpu + busy
                mark = ">" if pid == pids[choice] else " "
                if pid == pids[choice]:
                    select_row = len(lines)
                child = "+-" if int(sf[4]) in pids else ""    # child of a listed one

                # first read every thread (TCB), so the process line can
                # show the SUM of the context switches of all its threads
                try:
                    tids = sorted(os.listdir(path + "/task"), key=int)
                except OSError:
                    tids = []
                total_threads = total_threads + len(tids)
                thread_lines = []
                all_switches = 0
                for tid in tids:
                    tf = read_stat(path + "/task/" + tid)
                    ts = read_status(path + "/task/" + tid)
                    if not tf:
                        continue
                    tbusy = cpu_percent(previous, tid, int(tf[14]) + int(tf[15]), now)
                    switches = int(ts.get("voluntary_ctxt_switches", 0)) \
                        + int(ts.get("nonvoluntary_ctxt_switches", 0))
                    all_switches = all_switches + switches
                    thread_lines.append("     %-9s %-6s %-5s %-3s %4.0f%% %7.2f %7.2f %4s %9s %8d"
                                        % (tid + ("*" if tid == str(pid) else ""), "",
                                           tf[3], tf[39], tbusy, int(tf[14]) / TICKS,
                                           int(tf[15]) / TICKS, "", "", switches))

                lines.append("%s%-13s %-6s %-5s %-3s %4.0f%% %7.2f %7.2f %4s %9s %8d"
                             % (mark, child + str(pid), sf[4], sf[3], sf[39], busy,
                                int(sf[14]) / TICKS, int(sf[15]) / TICKS, sf[20],
                                st.get("VmRSS", "-"), all_switches))
                if len(thread_lines) > 1:       # one thread: the line above is enough
                    lines.extend(thread_lines)
            footer = ("TOTAL: %d process(es), %d thread(s), CPU %.0f%%   "
                      "(this computer: %d cores = %d%%)"
                      % (len(pids), total_threads, total_cpu,
                         os.cpu_count(), os.cpu_count() * 100))

            # keep the selected process on screen if the list is long
            room = height - 6                   # rows for the table body
            body = lines[4:]
            if len(body) > room:
                start = 0
                if select_row - 4 >= room:
                    start = min(select_row - 4, len(body) - room)
                lines = lines[:4] + body[start:start + room]
            lines.append("")
            lines.append(footer)
        else:
            choice = choice % len(pids)
            pid = pids[choice]
            path = "/proc/%d" % pid
            st = read_status(path)
            sf = read_stat(path)
            if not sf:
                continue                    # it just exited, try again

            uptime = float(read_text("/proc/uptime").split()[0])
            age = uptime - int(sf[22]) / TICKS
            fds = []
            try:
                for fd in sorted(os.listdir(path + "/fd"), key=int):
                    fds.append("%s->%s" % (fd, os.readlink(path + "/fd/" + fd)))
            except OSError:
                pass
            maps = len(read_text(path + "/maps").splitlines())
            kids = children.get(pid, [])
            parent = int(sf[4])

            # context switches of the whole process = sum over all its threads
            vol = 0
            invol = 0
            try:
                for tid in os.listdir(path + "/task"):
                    ts = read_status(path + "/task/" + tid)
                    vol = vol + int(ts.get("voluntary_ctxt_switches", 0))
                    invol = invol + int(ts.get("nonvoluntary_ctxt_switches", 0))
            except OSError:
                pass

            lines.append("DETAIL  '%s'  process %d of %d   [n]ext [p]rev [a]ll [q]uit"
                         % (word, choice + 1, len(pids)))
            lines.append("")
            lines.append("== PROCESS CONTROL BLOCK (PCB) ==   from /proc/%d/" % pid)
            lines.append("Identity : PID %d   PPID %d (%s)   UID %s   Name %s"
                         % (pid, parent, names.get(parent, "?"),
                            st.get("Uid", "?").split()[0], st.get("Name", "?")))
            lines.append("Command  : " + read_text(path + "/cmdline").replace("\0", " "))
            lines.append("State    : %-14s Threads %-4s Started %.1f s ago   Children %s"
                         % (st.get("State", "?"), st.get("Threads", "?"), age,
                            kids[:6] if kids else "none"))
            lines.append("Schedule : last CPU %-3s priority %-4s nice %-4s policy %s"
                         % (sf[39], sf[18], sf[19], POLICY.get(int(sf[41]), sf[41])))
            lines.append("CPU time : user %.2f s  system %.2f s  "
                         "switches: vol %s, invol %s"
                         % (int(sf[14]) / TICKS, int(sf[15]) / TICKS, vol, invol))
            lines.append("Memory   : virtual %s   resident %s   data %s   stack %s   maps %d"
                         % (st.get("VmSize", "-"), st.get("VmRSS", "-"),
                            st.get("VmData", "-"), st.get("VmStk", "-"), maps))
            lines.append("Files    : %d open   %s" % (len(fds), "  ".join(fds)))
            lines.append("Signals  : blocked %s  caught %s"
                         % (st.get("SigBlk", "?"), st.get("SigCgt", "?")))
            lines.append("== THREAD CONTROL BLOCKS (TCB) ==   from /proc/%d/task/<TID>/" % pid)
            lines.append("%-8s %-15s %-5s %-3s %5s %7s %7s %8s %8s"
                         % ("TID", "NAME", "STATE", "CPU", "CPU%", "USER s", "SYS s",
                            "VOL_CS", "INVOL_CS"))

            try:
                tids = sorted(os.listdir(path + "/task"), key=int)
            except OSError:
                tids = []
            room = height - len(lines) - 2      # rows left for threads
            for tid in tids[:room]:
                tpath = path + "/task/" + tid
                tf = read_stat(tpath)
                ts = read_status(tpath)
                if not tf:
                    continue
                busy = cpu_percent(previous, tid, int(tf[14]) + int(tf[15]), now)
                lines.append("%-8s %-15s %-5s %-3s %4.0f%% %7.2f %7.2f %8s %8s"
                             % (tid + ("*" if tid == str(pid) else ""), tf[2], tf[3],
                                tf[39], busy, int(tf[14]) / TICKS, int(tf[15]) / TICKS,
                                ts.get("voluntary_ctxt_switches", "?"),
                                ts.get("nonvoluntary_ctxt_switches", "?")))
            if len(tids) > room:
                lines.append("... and %d more thread(s): make the terminal taller"
                             % (len(tids) - room))
            lines.append("* = main thread (its TID is the same as the PID)")

        # ---- draw: cut every line to the screen size ----
        screen.erase()
        for row in range(min(len(lines), height)):
            screen.addstr(row, 0, lines[row][:width - 1])
        screen.refresh()

        key = screen.getch()                # waits up to 1 second
        if key in (ord("q"), ord("Q")):
            break
        if key in (ord("n"), ord("N"), curses.KEY_DOWN):
            choice = choice + 1
        if key in (ord("p"), ord("P"), curses.KEY_UP):
            choice = choice - 1
        if key in (ord("d"), ord("D"), 10, curses.KEY_ENTER):
            view = "detail"
        if key in (ord("a"), ord("A")):
            view = "all"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 pcbview.py <part of command, or PID>")
        print("   e.g. python3 pcbview.py matmul")
        sys.exit(1)
    if not os.path.isdir("/proc/self/task"):
        print("This program needs Linux (/proc).")
        sys.exit(1)
    curses.wrapper(main, sys.argv[1])


