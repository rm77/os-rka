#!/bin/sh

echo "=== OBSERVE A PROCESS THROUGH /proc ==="
echo

echo "This script PID = $$"
echo

echo "Selected information from /proc/$$/status:"
echo

grep -E '^(Name|State|Pid|PPid|Threads):' "/proc/$$/status"

echo
echo "Key idea:"
echo "/proc exposes information maintained by the Linux kernel."
echo "It lets us observe a process while it exists."
