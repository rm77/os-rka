#!/bin/sh
echo "=== PCI DEVICES ==="
if command -v lspci >/dev/null 2>&1; then
    lspci
else
    echo "lspci is unavailable. Install: apk add pciutils"
fi
