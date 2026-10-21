# Security & Isolation Limitations

This document outlines the security boundaries, limitations, and intended threat model of Mini Docker.

---

## 1. Educational Purpose Notice

Mini Docker is built exclusively as an **academic, educational tool** for the Operating Systems course at VIT Vellore. It illustrates how Linux kernel primitives operate together to create containerized environments.

**It is NOT designed, verified, or hardened as a production container sandbox.**

---

## 2. Inherent Limitations of `chroot`

A frequent misconception in container discussions is equating `chroot` with a secure sandbox:

1. **Root Can Break Chroot**: If a process inside a `chroot` runs as `root` (UID 0) without dropping capabilities (`CAP_SYS_CHROOT`), it can create a nested directory, chroot into it, and traverse back up to the real host root using `..`.
2. **Device Nodes**: Without mounting a private `devtmpfs` or masking `/dev`, a container process with sufficient privileges could access raw host disk partitions (e.g. `/dev/sda`).
3. **Mount Leakage**: Without setting mount propagation flags to `MS_PRIVATE`, mounts executed inside the container would be visible and active on the host system.

Mini Docker demonstrates the baseline requirements (e.g., Mount namespaces, `MS_PRIVATE` propagation, and `chdir("/")` after `chroot`), but does not implement comprehensive device cgroup whitelisting (`devices.allow`).

---

## 3. Privilege Model & Kernel Attack Surface

1. **Shared Kernel**: All container processes execute directly on the host Linux kernel. Any kernel vulnerability or unhandled system call could allow container breakout.
2. **Missing Seccomp / AppArmor Profiles**: Production engines (Docker, Podman) apply default seccomp BPF filters blocking hundreds of dangerous syscalls (such as `kexec_load`, `ptrace`, `sys_rawio`). Mini Docker intentionally does not install seccomp filters so students can inspect bare system calls.
3. **Host Root Filesystems**: Never mount untrusted third-party rootfs directories or run untrusted binaries using Mini Docker.

---

## 4. Comparison with Production Runtimes

| Feature | Mini Docker | Production Container (runc / Docker) |
| :--- | :--- | :--- |
| **Primary Goal** | Educational clarity & simplicity | Multi-tenant security & OCI compliance |
| **Seccomp BPF Filter** | None | Over 300 dangerous syscalls blocked |
| **Capabilities Dropping** | Inherited from launcher | Explicitly dropped (e.g. CAP_SYS_ADMIN dropped) |
| **Device Whitelisting** | None | Strictly filtered via cgroup v2 / ebpf |
| **Storage Layers** | Flat directory | Copy-on-Write (OverlayFS / snapshotter) |
| **Networking** | Basic private stack | veth pairs, bridge, NAT, firewall filtering |
