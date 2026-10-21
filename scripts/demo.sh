#!/usr/bin/env bash
set -uo pipefail

BIN="./bin/mini-docker"
ROOTFS="./tests/fixtures/rootfs"

echo "=================================================================="
echo "          MINI DOCKER CONTAINER ENGINE - LIVE DEMONSTRATION       "
echo "=================================================================="

echo -e "\n[Demo 1] Preflight Environment and Capability Check:"
$BIN check

echo -e "\n------------------------------------------------------------------"
echo "[Demo 2] Baseline Command Execution and Argument Handling:"
$BIN run -- /bin/echo "Hello from isolated container process!" "Arg with spaces"

echo -e "\n------------------------------------------------------------------"
echo "[Demo 3] Child Process Exit Code Propagation:"
echo "Running command that exits with code 42..."
set +e
$BIN run -- /bin/sh -c "exit 42"
EXIT_CODE=$?
set -e
echo "Propagated exit status code: $EXIT_CODE (Expected: 42)"

echo -e "\n------------------------------------------------------------------"
echo "[Demo 4] Hostname Isolation via UTS Namespace:"
echo "Host hostname: $(hostname)"
if [ "$(id -u)" -eq 0 ]; then
    echo "Running container with hostname 'demo-node-01'..."
    $BIN run --uts --hostname demo-node-01 -- /bin/hostname
    echo "Host hostname after container exit: $(hostname)"
else
    echo "Note: UTS namespace with sethostname requires root/sudo. Run with sudo for live test."
fi

echo -e "\n------------------------------------------------------------------"
echo "[Demo 5] Process ID Isolation via PID Namespace:"
if [ "$(id -u)" -eq 0 ]; then
    echo "Executing command in isolated PID namespace..."
    $BIN run --pid -- /bin/sh -c 'echo "PID inside container: $$"'
else
    echo "Note: PID namespace creation requires root/sudo. Run with sudo for live test."
fi

echo -e "\n------------------------------------------------------------------"
echo "[Demo 6] Filesystem Isolation with Rootfs:"
if [ ! -f "$ROOTFS/bin/init" ]; then
    ./scripts/setup_test_rootfs.sh
fi
if [ "$(id -u)" -eq 0 ]; then
    echo "Executing isolated binary within custom root filesystem..."
    $BIN run --rootfs "$ROOTFS" -- /bin/init
else
    echo "Note: Mount & chroot isolation requires root/sudo. Run with sudo for live test."
fi

echo -e "\n------------------------------------------------------------------"
echo "[Demo 7] Resource Controls via cgroup v2 (Memory & CPU Quota):"
if [ "$(id -u)" -eq 0 ]; then
    $BIN run -v --memory 64M --cpu-quota 50000 -- /bin/echo "Resource constraints active!"
else
    echo "Note: cgroup v2 writing requires root/sudo. Run with sudo for live test."
fi

echo -e "\n=================================================================="
echo "                   DEMONSTRATION COMPLETED                        "
echo "=================================================================="
