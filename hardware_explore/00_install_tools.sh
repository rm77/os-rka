#!/bin/sh
echo "Updating Alpine package index..."
apk update
echo "Installing inspection tools..."
apk add util-linux pciutils usbutils iproute2 procps-ng
echo "Done."
