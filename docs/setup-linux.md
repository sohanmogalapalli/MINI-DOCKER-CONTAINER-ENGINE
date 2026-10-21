# Linux Setup & Environment Prerequisites

This guide explains how to prepare, build, and test Mini Docker on various Linux environments and WSL2.

---

## 1. Supported Environments

Mini Docker requires Linux kernel version **5.8 or higher** (kernel 6.x recommended) with:
- Unified cgroup v2 enabled at `/sys/fs/cgroup`.
- Kernel namespaces compiled in (`CONFIG_NAMESPACES=y`, `CONFIG_UTS_NS=y`, `CONFIG_PID_NS=y`, `CONFIG_USER_NS=y`, `CONFIG_NET_NS=y`).

Tested and verified on:
- **Ubuntu 22.04 LTS / 24.04 LTS / 25.10 / Resolute**
- **WSL2 on Windows 10/11** (Ubuntu distribution)
- **Debian GNU/Linux 12 (Bookworm)**
- **Fedora 39+**

---

## 2. Toolchain Prerequisites

Install standard build utilities and the GCC C compiler:

```bash
# Ubuntu / Debian
sudo apt-get update
sudo apt-get install -y build-essential make gcc git python3

# Fedora / RHEL
sudo dnf install -y make gcc git python3

# Arch Linux
sudo pacman -S --needed base-devel git python
```

---

## 3. Kernel & Cgroup Configuration

Check your current environment using the built-in diagnostic tool:

```bash
make
./bin/mini-docker check
```

Expected output confirms:
- Kernel version (e.g. `Linux 6.x`).
- Supported namespaces: UTS, PID, Mount, IPC, Net, User.
- Unified cgroup v2 mounted at `/sys/fs/cgroup` with active `memory` and `cpu` controllers.

### WSL2 Users Note
WSL2 provides a full Linux kernel running inside a lightweight Hyper-V utility VM. cgroup v2 and all standard namespaces are natively supported out of the box.

---

## 4. Privilege Boundaries & Execution Modes

Mini Docker operates in two capability tiers:

### Tier 1: Unprivileged Mode (Normal User)
- Commands that do not modify kernel namespace tables or sysfs cgroups can be run by any non-root user.
- Argument preservation, exit code propagation, error checking, help/version, and unit tests execute completely without `sudo`.
- Running privileged integration tests in this mode will safely output `[SKIP]` with an explanation, preserving test harness integrity.

### Tier 2: Privileged Mode (`sudo` or Root)
- Linux requires `CAP_SYS_ADMIN` capability to invoke `unshare(CLONE_NEWUTS | CLONE_NEWPID | CLONE_NEWNS)` and write to `/sys/fs/cgroup`.
- To test the complete suite of isolation features:
  ```bash
  sudo ./scripts/run_tests.sh
  sudo ./scripts/demo.sh
  ```

---

## 5. Non-Destructive Operation Guarantee

Mini Docker **never**:
- Recursively deletes user directories.
- Modifies host firewall rules or sysctl tunables.
- Writes to `/sys/fs/cgroup` outside of its own dedicated `mini-docker` subfolder.
- Modifies host hostname or host root filesystem.
