#!/bin/sh

echo "=== CREATE A CHILD PROCESS ==="
echo

echo "This script is the parent process."
echo "Parent PID = $$"
echo

echo "Starting: sleep 15"
sleep 15 &
CHILD_PID=$!

echo "Child PID = $CHILD_PID"
echo

echo "Parent and child:"
ps -o pid,ppid,stat,cmd -p $$ -p "$CHILD_PID"

echo
echo "Observe:"
echo "- parent and child have different PIDs"
echo "- the child's PPID should point to this script"
echo

echo "Waiting for the child to finish..."
wait "$CHILD_PID"

echo
echo "The child has terminated."
