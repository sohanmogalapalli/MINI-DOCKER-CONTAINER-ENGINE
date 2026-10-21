# Testing Strategy & Acceptance Verification

This document describes the test strategy, execution modes, test suite organization, and verified results.

---

## 1. Test Architecture

The test suite is organized into two primary tiers:

```text
tests/
├── unit/
│   ├── test_config.c            # Configuration parsing, memory strings, CPU limits
│   └── test_cgroups_config.c    # Cgroup v2 probing & context creation
└── integration/
    ├── test_run.sh              # Baseline command execution & space preservation
    ├── test_exit_status.sh      # Exit code propagation & missing binary rejection
    ├── test_hostname_namespace.sh # UTS namespace hostname isolation
    ├── test_pid_namespace.sh    # PID namespace isolation (PID 1 verification)
    ├── test_rootfs.sh           # Rootfs chroot & filesystem isolation
    └── test_cgroups.sh          # Cgroup v2 memory & CPU quota enforcement
```

---

## 2. Test Execution Commands

### Run All Tests (Unit + Integration)
```bash
make test
```

### Run Unit Tests Only (Unprivileged)
```bash
make test-unit
```

### Run Full Privileged Suite (Root / Sudo)
```bash
sudo ./scripts/run_tests.sh
```

---

## 3. Skip Behavior Policy

As required by the project specification, tests that depend on system capabilities (`CAP_SYS_ADMIN` or root cgroup write permissions) automatically detect the environment:
- If run without root privileges, the test outputs `[SKIP]` along with the exact explanation.
- A skipped test is **never** counted as a false pass or false failure.
- When run under `sudo`, all tests run and assert expected isolation behavior.

---

## 4. Verified Test Results

Recorded run on Ubuntu Linux kernel `6.18.33.2-microsoft-standard-WSL2` (x86_64):

```text
==========================================================
          Mini Docker Container Engine Test Suite         
==========================================================

--- [1/2] Running Unit Tests ---
Running unit tests for configuration parser...
Tests completed: 17 / 17 passed.
Running unit tests for cgroups...
  [probe] cgroup2 mounted: YES
  [probe] memory controller: YES
  [probe] cpu controller: YES
Cgroups tests completed: 2 / 2 passed.

--- [2/2] Running Integration Tests ---
=== Running test_cgroups.sh ===
[PASS] cgroup v2 memory and CPU limits applied and cleaned up cleanly
=== test_cgroups.sh PASSED ===
=== Running test_exit_status.sh ===
[PASS] Exit status 0 propagation
[PASS] Non-zero exit status 42 propagation
[PASS] Missing executable rejection
=== test_exit_status.sh PASSED ===
=== Running test_hostname_namespace.sh ===
[PASS] UTS namespace hostname isolated (Host remains 'Sohan')
=== test_hostname_namespace.sh PASSED ===
=== Running test_pid_namespace.sh ===
[PASS] PID namespace isolated (Container process is PID 1)
=== test_pid_namespace.sh PASSED ===
=== Running test_rootfs.sh ===
Minimal rootfs initialized at ./tests/fixtures/rootfs
[PASS] Rootfs filesystem isolated and executable executed inside container root
=== test_rootfs.sh PASSED ===
=== Running test_run.sh ===
[PASS] Simple command execution
[PASS] Argument preservation with spaces
[PASS] Help and version output
=== test_run.sh PASSED ===

==========================================================
 ALL TESTS COMPLETED SUCCESSFULLY!
==========================================================
```
