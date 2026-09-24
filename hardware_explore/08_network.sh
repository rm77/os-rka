#!/bin/sh
echo "=== NETWORK ==="
if command -v ip >/dev/null 2>&1; then
    ip addr
    echo
    ip route
else
    echo "ip is unavailable. Install: apk add iproute2"
fi
