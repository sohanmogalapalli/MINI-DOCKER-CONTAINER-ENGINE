# Mini Docker Container Engine

> **A Lightweight Educational Container Runtime Using Linux Kernel Features**\
> Operating Systems Course Project — VIT Vellore (2026)

[![Build & Test](https://img.shields.io/badge/Build-Passing-brightgreen.svg)]()
[![Target OS](https://img.shields.io/badge/Platform-Linux%20%2F%20WSL2-blue.svg)]()
[![Standard](https://img.shields.io/badge/Language-C11%20POSIX-orange.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 1. Overview

**Mini Docker** is a minimalist, educational Linux container runtime written from scratch in C11. It demystifies modern containerization (like Docker and Podman) by demonstrating the core Operating System primitives that make containers possible:

- **Process Isolation**: Process tree isolation using **Linux PID namespaces** (the child process sees itself as PID 1).
- **Hostname Isolation**: Domain and host isolation via **UTS namespaces**.
- **Filesystem Isolation**: Independent mount tables (**Mount namespaces**), private mount propagation, and root filesystem switching via `chroot`.
- **Resource Control**: Kernel-enforced memory and CPU limits using **cgroup v2** (`memory.max` and `cpu.max`).
- **Process Supervision**: POSIX signal handling, robust `waitpid` with `EINTR` retry, and exit status propagation.

### What Mini Docker Is
- A small, transparent C codebase designed to explore Linux system call interfaces (`clone`, `unshare`, `mount`, `chroot`, `sethostname`).
- An educational tool for OS course students and educators.

### What Mini Docker Is Not
- **Not a Docker daemon replacement**: No client-server daemon, background service, or REST API.
- **Not an image registry client**: No Dockerfile parser, layered image storage (OverlayFS), or remote registry downloads.
- **Not a production security sandbox**: This project does not claim hardened multi-tenant isolation against hostile malicious payloads.

---

## 2. Feature Support Matrix

| Feature | Primitive Used | Status | Notes |
| :--- | :--- | :--- | :--- |
| **Command Execution** | `execvp`, `fork`, `waitpid` | **Implemented** | Argv-based execution, preserves spaces, no shell injection |
| **Exit Code Propagation** | `waitpid`, `WIFEXITED`, `WEXITSTATUS` | **Implemented** | Propagates 0-255 codes and signal status (128+N) |
| **UTS Namespace** | `unshare(CLONE_NEWUTS)`, `sethostname` | **Implemented** | Hostname changed inside container; host unchanged |
| **PID Namespace** | `unshare(CLONE_NEWPID)` + child fork | **Implemented** | Target process runs as PID 1 |
| **Mount Namespace** | `unshare(CLONE_NEWNS)`, `MS_PRIVATE` | **Implemented** | Private mount namespace, prevents propagation to host |
| **IPC Namespace** | `unshare(CLONE_NEWIPC)` | **Implemented** | Isolates POSIX/SysV message queues and semaphores |
| **Network Namespace** | `unshare(CLONE_NEWNET)` | **Implemented** | Isolates loopback/network stack |
| **Filesystem / Rootfs** | `mount(MS_BIND)`, `chroot`, `chdir` | **Implemented** | Validates directory, mounts `/proc` if present |
| **Memory Limit** | cgroup v2 `memory.max` | **Implemented** | Formats e.g. `64M`, `1G`; cleans up cgroup on exit |
| **CPU Limit** | cgroup v2 `cpu.max` | **Implemented** | Configures quota / period microsecond limits |
| **Environment Check** | Sysfs and `/proc/self/ns` inspection | **Implemented** | Read-only preflight diagnostic command |

---

## 3. Prerequisites & Development Environment

Mini Docker relies on Linux kernel interfaces. Supported environments:
- **Native Linux** (Ubuntu 22.04+, Debian 12+, Fedora, Arch)
- **WSL2 on Windows** (Ubuntu on WSL2 with Linux 5.15+ or 6.x kernel)
- **Linux Virtual Machine** (VirtualBox, VMware, QEMU/KVM)

### Required Packages (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y build-essential make gcc
```

---

## 4. Build Instructions

The project uses a standard, self-contained `Makefile` with strict compiler flags (`-Wall -Wextra -Wpedantic -Wshadow -Wconversion -Wformat=2`):

```bash
# Build the mini-docker binary and test executables
make

# Run the complete test suite (unit and integration tests)
make test

# Run environment preflight check
make check

# Clean all build artifacts
make clean
```

Executable binary will be placed at `bin/mini-docker`.

---

## 5. Quick Start & Usage

### 1. Preflight Environment Check
Verify your kernel, namespace availability, and cgroup v2 setup:
```bash
./bin/mini-docker check
```

### 2. Basic Command Execution
Run a command as an isolated child process:
```bash
./bin/mini-docker run -- /bin/echo "Hello from Mini-Docker!"
```

### 3. UTS Namespace (Hostname Isolation)
Run with a private hostname (requires root/sudo for `sethostname`):
```bash
sudo ./bin/mini-docker run --uts --hostname container-alpha -- /bin/hostname
```

### 4. PID Namespace (PID 1 Verification)
Verify that the container process sees itself as PID 1:
```bash
sudo ./bin/mini-docker run --pid -- /bin/sh -c 'echo "Inside container PID is: $$"'
```

### 5. Resource Limits with cgroup v2
Constrain memory to 64MB and CPU quota to 50ms per 100ms:
```bash
sudo ./bin/mini-docker run -v --memory 64M --cpu-quota 50000 -- /bin/echo "Constrained workload"
```

### 6. Filesystem Isolation (Rootfs)
Run inside a custom minimal root directory:
```bash
# Generate the minimal rootfs fixture
./scripts/setup_test_rootfs.sh

# Run inside rootfs
sudo ./bin/mini-docker run --rootfs ./tests/fixtures/rootfs -- /bin/init
```

### 7. Run Full Automated Demo
```bash
sudo ./scripts/demo.sh
```

---

## 6. Architecture & Code Layout

```
mini-docker/
├── Makefile                    # Build system with strict C11 flags
├── include/                    # Header declarations
│   ├── cli.h                   # Argument parsing & CLI options
│   ├── config.h                # Configuration struct & memory/cpu parsers
│   ├── error.h                 # Standardized error codes & perror wrappers
│   ├── log.h                   # Diagnostic & verbose logging
│   ├── namespaces.h            # Linux namespace probing and application
│   ├── filesystem.h            # Rootfs validation, bind mounts, and chroot
│   ├── cgroups.h               # cgroup v2 hierarchy, limits, and cleanup
│   ├── process.h               # Synchronization pipes, fork/exec, waitpid
│   └── runtime.h               # Central runtime orchestrator
├── src/                        # Implementations
│   ├── main.c                  # Minimal CLI entrypoint
│   ├── cli.c                   # CLI parser (getopt_long)
│   ├── config.c                # Validation & unit conversions
│   ├── error.c                 # Error messages
│   ├── log.c                   # Logging implementation
│   ├── namespaces.c            # Linux namespace system calls
│   ├── filesystem.c            # Filesystem isolation operations
│   ├── cgroups.c               # cgroup v2 filesystem writes & cleanup
│   ├── process.c               # Parent-child sync & execution
│   └── runtime.c               # Lifecycle orchestration
├── tests/
│   ├── unit/                   # Unit test executables
│   └── integration/            # Automated bash integration tests
├── scripts/                    # Helper and demo scripts
└── docs/                       # Comprehensive documentation
```

---

## 7. Security & Educational Limitations

> [!CAUTION]
> Mini Docker is created strictly for **educational demonstrations**. It is not a security sandbox.
> - `chroot` alone does not prevent a privileged process from escaping if devices or permissions are misconfigured.
> - Do not run untrusted or malicious binaries inside this runtime.
> - Kernel security modules (SELinux/AppArmor) and seccomp filters are left to host defaults and are not reconfigured by this runtime.

---

## 8. License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
