#!/bin/sh

echo "=== PROCESS LIFECYCLE ==="
echo

echo "1. Create a process"
sleep 5 &
PID=$!

echo "Created process PID = $PID"
echo

echo "2. Observe the process while it exists"
ps -o pid,ppid,stat,cmd -p "$PID"

echo
echo "The sleep process usually appears in state S."
echo "S means sleeping/waiting."
echo

echo "3. Wait for the process to finish"
wait "$PID"

echo
echo "4. Check again"
if ps -p "$PID" >/dev/null 2>&1
then
    echo "Process still exists."
else
    echo "Process no longer exists."
fi

echo
echo "Lifecycle observed:"
echo "created -> waiting/running -> terminated"
