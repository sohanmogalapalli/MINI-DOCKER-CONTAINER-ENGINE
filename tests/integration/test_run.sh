#!/usr/bin/env bash
set -euo pipefail

BIN="./bin/mini-docker"
echo "=== Running test_run.sh ==="

# 1. Simple command run
OUTPUT=$($BIN run -- /bin/echo "hello from container")
if [ "$OUTPUT" != "hello from container" ]; then
    echo "FAILED: expected 'hello from container', got '$OUTPUT'"
    exit 1
fi
echo "[PASS] Simple command execution"

# 2. Argument preservation with spaces
OUTPUT=$($BIN run -- /bin/echo "hello world" "arg two with space")
if [ "$OUTPUT" != "hello world arg two with space" ]; then
    echo "FAILED: arguments with spaces were not preserved"
    exit 1
fi
echo "[PASS] Argument preservation with spaces"

# 3. Help and version
$BIN --help > /dev/null
$BIN --version > /dev/null
echo "[PASS] Help and version output"

echo "=== test_run.sh PASSED ==="
