# Mini Docker Architecture & Internal Design

This document details the internal design, execution flow, synchronization mechanisms, and system call sequences of the Mini Docker container engine.

---

## 1. High-Level Architecture Overview

Mini Docker uses a clean, layered modular design separating the CLI, configuration validation, lifecycle orchestration, and low-level kernel interaction modules:

```text
       +---------------------------------------------+
       |             User Terminal / CLI             |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |           CLI Parser (cli.c)                |
       |      - getopt_long option decoding          |
       |      - Argument splitting via '--'          |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |       Configuration Validation (config.c)   |
       |      - Parse memory limits (e.g. 128M)      |
       |      - Parse CPU quotas & periods           |
       |      - Validate hostname and paths          |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |       Runtime Orchestrator (runtime.c)      |
       +---------------------------------------------+
             |                     |               |
             v                     v               v
  +--------------------+  +----------------+  +-----------------+
  | Namespaces Setup   |  | Cgroups v2     |  | Filesystem/Root |
  | (namespaces.c)     |  | (cgroups.c)    |  | (filesystem.c)  |
  | - CLONE_NEWUTS     |  | - memory.max   |  | - MS_PRIVATE    |
  | - CLONE_NEWPID     |  | - cpu.max      |  | - bind mount    |
  | - CLONE_NEWNS      |  | - cgroup.procs |  | - /proc mount   |
  | - CLONE_NEWIPC     |  | - cleanup      |  | - chroot/chdir  |
  +--------------------+  +----------------+  +-----------------+
             |                     |               |
             +---------------------+---------------+
                                   |
                                   v
       +---------------------------------------------+
       |       Process Lifecycle Manager (process.c) |
       |      - Parent/Child Sync Pipes              |
       |      - execvp argv execution                |
       |      - waitpid & signal forwarding          |
       +---------------------------------------------+
```

---

## 2. Process Lifecycle & Execution Flow

### 2.1 The Two-Phase PID Namespace Model

In Linux, calling `unshare(CLONE_NEWPID)` alters the PID namespace for **future child processes**, not for the caller itself. Therefore, to make the container's main command run as **PID 1**, Mini Docker employs a clean two-step hierarchy:

```
[Host / Parent Process]
         |
         | fork()
         v
   [Child 1 (Bridge Process)]
         |
         | unshare(CLONE_NEWPID | CLONE_NEWUTS | CLONE_NEWNS ...)
         | sethostname(...)
         | fork()
         v
   [Child 2 (Container PID 1)]
         |
         |-- sync_pipe: Wait for Parent to apply cgroup limits
         |-- fs_setup: MS_PRIVATE bind mount, mount /proc, chroot, chdir("/")
         |-- execvp(command_argv)
```

1. **Host Parent Process**:
   - Manages the supervisor loop.
   - Creates the bidirectional synchronization pipes (`pipe2(O_CLOEXEC)`).
   - Once Child 1 (or Child 2) is created, configures cgroup v2 limit files (`memory.max`, `cpu.max`) and writes the PID into `cgroup.procs`.
   - Sends the release token (`'G'`) over the pipe to allow the child to proceed.
   - Waits for the child using `waitpid` with `EINTR` loop handling.
   - Traps `SIGINT` / `SIGTERM` and forwards them to the child.
   - Deletes the ephemeral cgroup directory upon exit.

2. **Child 1 (Bridge Process)**:
   - Enters the requested namespaces via `unshare()`.
   - Calls `fork()` to spawn Child 2 into the newly created PID namespace.
   - Child 1 waits for Child 2 and translates its exit status directly to the Parent.

3. **Child 2 (Target Workload / PID 1)**:
   - Sees `getpid() == 1`.
   - Blocks on the sync pipe until the parent has confirmed cgroup attachment.
   - Executes filesystem isolation (`fs_setup_rootfs`).
   - Invokes `execvp` with the target binary and arguments.

---

## 3. Parent-Child Synchronization Mechanism

To prevent race conditions where a fast-running child executes and finishes *before* the parent has attached it to cgroup v2 limits, Mini Docker uses a dedicated synchronization handshake:

```text
Child 2 (or Child)                             Parent
       |                                          |
       |--- Write 'R' (Ready) ------------------->|
       |                                          | [Parent detects Child PID]
       |                                          | [Creates cgroup directory]
       |                                          | [Writes memory.max & cpu.max]
       |                                          | [Writes child PID to cgroup.procs]
       |<-- Write 'G' (Go / Proceed) -------------|
       |                                          |
[Proceed to execvp]                        [Blocks in waitpid]
```

Both pipes are opened with `O_CLOEXEC` so they are automatically closed upon `execvp`, preventing file descriptor leaks into user programs.

---

## 4. Ordering Decisions & Kernel Invariants

The order of operations is crucial in Linux systems programming:

1. **Namespace Unsharing precedes Filesystem Configuration**:
   The mount namespace (`CLONE_NEWNS`) must be active before modifying mount propagation or mounting rootfs; otherwise, host mounts would be corrupted.
2. **Mount Propagation Isolation (`MS_PRIVATE`)**:
   Modern Linux distributions mount `/` as `shared` (`MS_SHARED`). Without explicitly setting `mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL)`, bind mounts and unmounts inside the container would leak back to the host system.
3. **Bind Mount before `chroot`**:
   The target rootfs path is bind-mounted onto itself to guarantee it is recognized by the kernel as an independent mountpoint.
4. **`chdir("/")` immediately after `chroot`**:
   Calling `chroot` only changes the root pointer in the process descriptor; it does not change the current working directory (`cwd`). Calling `chdir("/")` is mandatory to avoid remaining outside the new root.
5. **Cgroup Placement precedes User Execution**:
   A process cannot reliably restrict its own parent cgroup. The parent configures and attaches the child prior to user command execution.

---

## 5. Cleanup Invariants

- **Idempotent Resource Deletion**: The cgroup created (`/sys/fs/cgroup/mini-docker/container-<PID>`) is removed with `rmdir()` after the process terminates. A retry loop handles transient kernel refcount drainage.
- **No Orphan Children**: If child setup fails at any intermediate stage, the child terminates immediately with an error status code and the parent cleans up the allocated cgroups.
