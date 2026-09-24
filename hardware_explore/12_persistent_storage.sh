#!/bin/sh
echo "=== PERSISTENT STORAGE ==="
echo "Persistent data location: /home/sisop"
echo
if [ -d /home/sisop ]; then
    df -h /home/sisop
else
    echo "/home/sisop is not available."
fi
