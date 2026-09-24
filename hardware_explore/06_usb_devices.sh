#!/bin/sh
echo "=== USB DEVICES ==="
if command -v lsusb >/dev/null 2>&1; then
    lsusb
else
    echo "lsusb is unavailable. Install: apk add usbutils"
fi
