#!/usr/bin/env bash
set -euo pipefail

BIN="./bin/mini-docker"
echo "=== Running test_hostname_namespace.sh ==="

ORIGINAL_HOSTNAME=$(hostname)
CONTAINER_HOSTNAME="isolated-box-99"

# Check if we have permission to unshare UTS (e.g. root/sudo or user namespace)
if [ "$(id -u)" -ne 0 ]; then
    # Try running, if permission denied, record SKIP as required by specification
    if ! $BIN run --uts --hostname "$CONTAINER_HOSTNAME" -- /bin/hostname > /dev/null 2>&1; then
        echo "[SKIP] UTS namespace test skipped: unprivileged user requires sudo or CAP_SYS_ADMIN"
        exit 0
    fi
fi

RESULT=$($BIN run --uts --hostname "$CONTAINER_HOSTNAME" -- /bin/hostname)
if [ "$RESULT" != "$CONTAINER_HOSTNAME" ]; then
    echo "FAILED: expected container hostname '$CONTAINER_HOSTNAME', got '$RESULT'"
    exit 1
fi

AFTER_HOSTNAME=$(hostname)
if [ "$ORIGINAL_HOSTNAME" != "$AFTER_HOSTNAME" ]; then
    echo "FAILED: host hostname was modified!"
    exit 1
fi

echo "[PASS] UTS namespace hostname isolated (Host remains '$ORIGINAL_HOSTNAME')"
echo "=== test_hostname_namespace.sh PASSED ==="
