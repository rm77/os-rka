#!/bin/sh
echo "=== PROCESSES ==="
if command -v ps >/dev/null 2>&1; then
    ps -e
else
    echo "ps is unavailable. Install: apk add procps-ng"
fi
echo
echo "Number of active process directories:"
find /proc -maxdepth 1 -type d -name '[0-9]*' 2>/dev/null | wc -l
