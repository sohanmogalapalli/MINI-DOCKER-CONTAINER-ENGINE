# Troubleshooting Guide

Common issues, failure diagnostics, and remediation steps.

---

## 1. "Namespace creation denied (EPERM)"

### Symptoms
```text
[mini-docker] ERROR: Namespace creation denied (EPERM). Privilege (root/sudo) or user namespace capability required.
```

### Cause
Calling `unshare()` for UTS, PID, Mount, or IPC namespaces requires the `CAP_SYS_ADMIN` capability in the current user namespace.

### Solution
- Run with `sudo`:
  ```bash
  sudo ./bin/mini-docker run --uts --hostname testbox -- /bin/hostname
  ```
- Alternatively, run in a Linux environment or container where user namespaces are enabled.

---

## 2. "Failed to create cgroup parent ... Permission denied"

### Symptoms
```text
[mini-docker] ERROR: Failed to create cgroup parent at /sys/fs/cgroup/mini-docker. Privilege or delegation required.
```

### Cause
On Linux systems using systemd and cgroup v2, the root cgroup `/sys/fs/cgroup` is owned by `root:root` and mode `0755`. Unprivileged users cannot write directly to it.

### Solution
- Run with `sudo`:
  ```bash
  sudo ./bin/mini-docker run --memory 64M -- /bin/echo "Works"
  ```
- Or specify a user-delegated cgroup directory via `--cgroup-parent /sys/fs/cgroup/user.slice/user-1000.slice/...`

---

## 3. "Command not found" or "No such file or directory" inside `--rootfs`

### Symptoms
```text
[mini-docker] ERROR: execvp: No such file or directory (errno=2)
```

### Cause
When `--rootfs` is supplied, the process root is moved to that directory. If you invoke `/bin/sh` or `/bin/ls`, those binaries (and their required dynamic linker and shared libraries like `libc.so.6`) must exist inside the target rootfs.

### Solution
- Use the provided static test fixture:
  ```bash
  ./scripts/setup_test_rootfs.sh
  sudo ./bin/mini-docker run --rootfs ./tests/fixtures/rootfs -- /bin/init
  ```
- Or unpack a full Alpine Linux mini-rootfs containing `/bin/busybox` and musl libc into your target rootfs directory.

---

## 4. `make: command not found`

### Solution
Install make and build tools:
```bash
sudo apt-get update && sudo apt-get install -y build-essential make
```
