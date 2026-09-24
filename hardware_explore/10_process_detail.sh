#!/bin/sh
echo "=== PROCESS DETAILS ==="
printf "%-6s %-20s %-8s %s\n" "PID" "NAME" "THREADS" "STATE"
for p in /proc/[0-9]*; do
    if [ -r "$p/status" ]; then
        pid=${p#/proc/}
        name=$(grep '^Name:' "$p/status" | awk '{print $2}')
        threads=$(grep '^Threads:' "$p/status" | awk '{print $2}')
        state=$(grep '^State:' "$p/status" | cut -f2-)
        printf "%-6s %-20s %-8s %s\n" "$pid" "$name" "$threads" "$state"
    fi
done
