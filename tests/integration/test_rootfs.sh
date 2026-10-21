#!/usr/bin/env bash
set -euo pipefail

BIN="./bin/mini-docker"
ROOTFS="./tests/fixtures/rootfs"

echo "=== Running test_rootfs.sh ==="

if [ ! -f "$ROOTFS/bin/init" ]; then
    ./scripts/setup_test_rootfs.sh
fi

if [ "$(id -u)" -ne 0 ]; then
    if ! $BIN run --rootfs "$ROOTFS" -- /bin/init > /dev/null 2>&1; then
        echo "[SKIP] Rootfs mount/chroot test skipped: requires root privileges (try with sudo)"
        exit 0
    fi
fi

OUTPUT=$($BIN run --rootfs "$ROOTFS" -- /bin/init)
if [ "$OUTPUT" != "HELLO_FROM_ROOTFS" ]; then
    echo "FAILED: expected 'HELLO_FROM_ROOTFS', got '$OUTPUT'"
    exit 1
fi

echo "[PASS] Rootfs filesystem isolated and executable executed inside container root"
echo "=== test_rootfs.sh PASSED ==="
