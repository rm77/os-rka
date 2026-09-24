#!/bin/sh

echo "=== ONE PROGRAM, MANY PROCESSES ==="
echo

echo "Starting the same program three times:"
echo "  sleep 20"
echo

sleep 20 &
P1=$!

sleep 20 &
P2=$!

sleep 20 &
P3=$!

echo "Process 1 PID = $P1"
echo "Process 2 PID = $P2"
echo "Process 3 PID = $P3"
echo

ps -o pid,ppid,stat,cmd -p "$P1" -p "$P2" -p "$P3"

echo
echo "Observe:"
echo "- the command is the same"
echo "- the PIDs are different"
echo
echo "Conclusion:"
echo "One stored program can create many separate processes."

echo
echo "Cleaning up..."
kill "$P1" "$P2" "$P3" 2>/dev/null
wait "$P1" 2>/dev/null
wait "$P2" 2>/dev/null
wait "$P3" 2>/dev/null

echo "Done."
