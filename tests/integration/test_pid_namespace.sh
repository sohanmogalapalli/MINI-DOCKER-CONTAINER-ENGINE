#!/usr/bin/env bash
set -euo pipefail

BIN="./bin/mini-docker"
echo "=== Running test_pid_namespace.sh ==="

# Check if we have permission to unshare PID
if [ "$(id -u)" -ne 0 ]; then
    if ! $BIN run --pid -- /bin/sh -c 'exit 0' > /dev/null 2>&1; then
        echo "[SKIP] PID namespace test skipped: unprivileged user requires sudo or CAP_SYS_ADMIN"
        exit 0
    fi
fi

# In a separate PID namespace, the root process of the container is PID 1
CHILD_PID=$($BIN run --pid -- /bin/sh -c 'echo $$')
if [ "$CHILD_PID" != "1" ]; then
    echo "FAILED: expected PID inside container to be 1, got '$CHILD_PID'"
    exit 1
fi

echo "[PASS] PID namespace isolated (Container process is PID 1)"
echo "=== test_pid_namespace.sh PASSED ==="
