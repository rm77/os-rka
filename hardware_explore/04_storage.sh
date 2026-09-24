#!/bin/sh
echo "=== STORAGE AND FILESYSTEMS ==="
if command -v lsblk >/dev/null 2>&1; then
    lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
else
    echo "lsblk is unavailable. Install: apk add util-linux"
fi
echo
df -h
if command -v findmnt >/dev/null 2>&1; then
    echo
    findmnt
fi
