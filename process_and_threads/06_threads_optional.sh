#!/bin/sh

echo "=== OPTIONAL: OBSERVE THREADS ==="
echo

if ! command -v python3 >/dev/null 2>&1
then
    echo "python3 is not installed."
    echo "Skip this optional activity."
    exit 0
fi

python3 - <<'PY' &
import threading
import time

def worker():
    time.sleep(15)

threads = []
for _ in range(3):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)

for t in threads:
    t.join()
PY

PID=$!

sleep 1

echo "Process PID = $PID"
echo
echo "Process view:"
ps -o pid,ppid,stat,nlwp,cmd -p "$PID"

echo
echo "Thread view:"
ps -T -p "$PID"

echo
echo "Key idea:"
echo "One process can contain multiple threads."
echo "Threads are separate execution paths inside the same process."

wait "$PID"
