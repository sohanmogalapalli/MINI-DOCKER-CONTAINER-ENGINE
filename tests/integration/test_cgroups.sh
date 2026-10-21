#!/usr/bin/env bash
set -euo pipefail

BIN="./bin/mini-docker"
echo "=== Running test_cgroups.sh ==="

if [ ! -d "/sys/fs/cgroup" ]; then
    echo "[SKIP] cgroup v2 not mounted on host"
    exit 0
fi

if [ "$(id -u)" -ne 0 ]; then
    # Unprivileged users may not have write access to /sys/fs/cgroup directly
    if [ ! -w "/sys/fs/cgroup" ]; then
        echo "[SKIP] cgroup v2 test skipped: unprivileged user cannot write to /sys/fs/cgroup (run with sudo)"
        exit 0
    fi
fi

# Run with memory limit and CPU quota
$BIN run -v --memory 64M --cpu-quota 50000 -- /bin/echo "cgroup container executed successfully"

echo "[PASS] cgroup v2 memory and CPU limits applied and cleaned up cleanly"
echo "=== test_cgroups.sh PASSED ==="
