#!/bin/sh
echo "=== PROCESSOR ==="
if command -v lscpu >/dev/null 2>&1; then
    lscpu
else
    echo "lscpu is unavailable. Install: apk add util-linux"
    cat /proc/cpuinfo
fi
