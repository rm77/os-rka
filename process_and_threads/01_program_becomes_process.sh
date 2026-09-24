#!/bin/sh

echo "=== PROGRAM -> PROCESS ==="
echo

echo "This file is a stored program:"
echo "  $0"
echo

echo "When sh executes this file, it becomes part of a running process."
echo

echo "PID  = $$"
echo "PPID = $PPID"
echo

echo "Process information:"
ps -o pid,ppid,stat,cmd -p $$

echo
echo "Key idea:"
echo "A program is passive code."
echo "A process is a running instance managed by the operating system."
