#!/bin/sh

echo "=== BACKGROUND PROCESS EXPLORATION ==="
echo

echo "This activity uses worker.sh as a simple long-running program."
echo

echo "Starting worker.sh in the background..."
sh ./worker.sh > worker.log 2>&1 &
PID=$!

echo "Background process PID = $PID"
echo

echo "1. Examine the process with ps"
ps -o pid,ppid,stat,etime,cmd -p "$PID"

echo
echo "2. Examine selected kernel information from /proc"
if [ -r "/proc/$PID/status" ]
then
    grep -E '^(Name|State|Pid|PPid|Threads):' "/proc/$PID/status"
else
    echo "Cannot read /proc/$PID/status"
fi

echo
echo "3. Show recent output produced by the process"
sleep 3
tail -n 5 worker.log

echo
echo "4. Check whether the process is still alive"
if kill -0 "$PID" 2>/dev/null
then
    echo "PID $PID is still running."
else
    echo "PID $PID is no longer running."
fi

echo
echo "5. Terminate the process"
kill "$PID" 2>/dev/null
wait "$PID" 2>/dev/null

echo
echo "6. Check again"
if kill -0 "$PID" 2>/dev/null
then
    echo "PID $PID still exists."
else
    echo "PID $PID has terminated."
fi

echo
echo "Key idea:"
echo "A stored program becomes a process when the OS creates and manages an execution instance."
echo "The process has an identity, state, lifetime, and observable behavior."
