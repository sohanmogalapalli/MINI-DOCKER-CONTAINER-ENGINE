#!/usr/bin/env bash
set -uo pipefail

BIN="./bin/mini-docker"
echo "=== Running test_exit_status.sh ==="

# 1. Success exit status 0
$BIN run -- /bin/true
STATUS=$?
if [ $STATUS -ne 0 ]; then
    echo "FAILED: expected exit 0, got $STATUS"
    exit 1
fi
echo "[PASS] Exit status 0 propagation"

# 2. Non-zero exit status 42
$BIN run -- /bin/sh -c "exit 42"
STATUS=$?
if [ $STATUS -ne 42 ]; then
    echo "FAILED: expected exit 42, got $STATUS"
    exit 1
fi
echo "[PASS] Non-zero exit status 42 propagation"

# 3. Nonexistent binary
$BIN run -- /path/to/definitely/nonexistent/binary 2> /dev/null
STATUS=$?
if [ $STATUS -eq 0 ]; then
    echo "FAILED: expected failure for nonexistent binary, got 0"
    exit 1
fi
echo "[PASS] Missing executable rejection"

echo "=== test_exit_status.sh PASSED ==="
