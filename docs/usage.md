# Mini Docker CLI Usage Reference

This document provides a comprehensive command-line reference for `mini-docker`.

---

## 1. Syntax Overview

```text
mini-docker [GLOBAL OPTIONS] check
mini-docker [GLOBAL OPTIONS] run [RUN OPTIONS] -- COMMAND [ARGUMENTS...]
mini-docker --help
mini-docker --version
```

> **Note on `--` Separator:**
> Mini Docker strictly enforces `--` to delineate runtime configuration flags from the container command and its arguments. This prevents ambiguity and protects against command argument confusion.

---

## 2. Command Reference

### `check`
Inspects host kernel features, namespace support, and cgroup v2 controller availability.

**Example:**
```bash
./bin/mini-docker check
```

---

### `run`
Executes `COMMAND` with the specified isolation and resource constraints.

#### Run Options

| Option | Argument | Description |
| :--- | :--- | :--- |
| `--hostname` | `NAME` | Assigns an isolated hostname to the container. Automatically enables the UTS namespace. |
| `--uts` | *(none)* | Creates a new UTS (UNIX Timesharing System) namespace. |
| `--pid` | *(none)* | Creates a new PID namespace. The container's target process runs as PID 1. |
| `--mount` | *(none)* | Creates a new Mount namespace with private mount propagation. |
| `--ipc` | *(none)* | Creates a new IPC namespace isolating shared memory and POSIX message queues. |
| `--network` | *(none)* | Creates a new Network namespace with private network stack. |
| `--rootfs` | `PATH` | Specifies a prepared directory to use as the container root filesystem via `chroot`. |
| `--memory` | `LIMIT` | Restricts container memory allocation via cgroup v2 `memory.max` (e.g., `64M`, `128M`, `1G`). |
| `--cpu-quota`| `VALUE` | Restricts CPU usage via cgroup v2 `cpu.max` in microseconds per period (e.g., `50000`). |
| `--cgroup-parent`| `PATH` | Custom parent cgroup directory (default: `/sys/fs/cgroup/mini-docker`). |

#### Global Options

| Option | Short | Description |
| :--- | :--- | :--- |
| `--verbose` | `-v` | Enables verbose diagnostic output to stderr. |
| `--help` | `-h` | Displays usage summary. |
| `--version` | `-V` | Displays version and author information. |

---

## 3. Practical Examples

### Basic Execution with Preserved Arguments
```bash
./bin/mini-docker run -- /bin/echo "Operating Systems Project" "VIT Vellore"
```

### Isolated Hostname Demo
```bash
sudo ./bin/mini-docker run --uts --hostname container-alpha -- /bin/hostname
# Output: container-alpha
# Host hostname remains unchanged!
```

### Verifying PID 1 Inside Container
```bash
sudo ./bin/mini-docker run --pid -- /bin/sh -c 'echo "My PID is: $$"'
# Output: My PID is: 1
```

### Applying Memory Limits (64MB)
```bash
sudo ./bin/mini-docker run -v --memory 64M -- /bin/echo "Running within 64MB cgroup limit"
```

### Running with a Dedicated Rootfs
```bash
./scripts/setup_test_rootfs.sh
sudo ./bin/mini-docker run --rootfs ./tests/fixtures/rootfs -- /bin/init
# Output: HELLO_FROM_ROOTFS
```
