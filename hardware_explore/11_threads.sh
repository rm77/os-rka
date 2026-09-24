#!/bin/sh
echo "=== THREADS ==="
total=0
for p in /proc/[0-9]*; do
    if [ -d "$p/task" ]; then
        n=$(ls "$p/task" 2>/dev/null | wc -l)
        total=$((total + n))
    fi
done
echo "Total threads: $total"
echo
echo "Current shell PID: $$"
if [ -d "/proc/$$/task" ]; then
    echo "Thread IDs of current shell:"
    ls "/proc/$$/task"
fi
