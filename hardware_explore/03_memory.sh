#!/bin/sh
echo "=== MEMORY ==="
if command -v free >/dev/null 2>&1; then
    free -h
else
    echo "free is unavailable. Install: apk add procps-ng"
fi
echo
grep -E 'MemTotal|MemFree|MemAvailable|Buffers|Cached|SwapTotal' /proc/meminfo
