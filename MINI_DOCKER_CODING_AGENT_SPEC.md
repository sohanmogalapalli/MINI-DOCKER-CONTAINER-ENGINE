# Mini Docker Container Engine

## Implementation Specification for Coding Agents

> **Project type:** Operating Systems course project\
> **Institution:** VIT Vellore\
> **Academic year:** 2026\
> **Primary goal:** Build a small, educational Linux container runtime
> that demonstrates process isolation, filesystem isolation, and
> resource control using Linux kernel features.\
> **Important:** This is a learning project, not a Docker replacement or
> a production-grade security boundary.

------------------------------------------------------------------------

## 1. Instructions to Coding Agents

You are implementing **Mini Docker Container Engine**, a small container
runtime for an Operating Systems course. Work incrementally, preserve a
simple architecture, explain OS concepts in comments/docs where useful,
and make each milestone runnable and testable.

### Non-negotiable engineering rules

1.  **Target Linux.** This project depends on Linux-specific kernel
    interfaces. Do not pretend that native macOS or Windows supports the
    same behavior. WSL2 or a Linux VM may be used for development,
    subject to kernel and privilege limitations.
2.  **Use C as the primary language**, with the Linux/POSIX system-call
    interfaces. This keeps the implementation close to the OS concepts
    being demonstrated.
3.  **Do not use Docker, containerd, Podman, or an existing container
    runtime to implement the runtime.** They may be used only as
    optional references for concepts, never as the engine underneath
    this project.
4.  **No web frontend is required for the core deliverable.** The
    primary interface is a CLI. Do not introduce React, Next.js, Flask,
    Django, or a database unless the project owner explicitly changes
    the scope.
5.  **Do not claim a feature is implemented until code and tests
    demonstrate it.** Keep documentation status aligned with actual
    behavior.
6.  **Fail safely.** Validate arguments, check every system-call result,
    clean up child processes and temporary resources, and provide
    actionable error messages.
7.  **Do not run destructive or privileged setup automatically.** Never
    recursively delete an arbitrary path, change host-wide settings, or
    silently modify host cgroups/mounts. Require explicit configuration
    for privileged operations.
8.  **Do not describe `chroot` alone as a secure sandbox.** A root
    filesystem change is only one part of isolation and does not by
    itself provide a complete security boundary.
9.  Keep a clear distinction between **implemented**, **partially
    implemented**, and **planned** features.
10. Prefer small, reviewable commits and run tests after every
    meaningful change.

------------------------------------------------------------------------

## 2. Project Summary

### Title

**Mini Docker Container Engine --- A Lightweight Container Runtime Using
Linux Kernel Features**

### Problem statement

Applications running directly on a shared host can interfere with each
other through process visibility, filesystem assumptions, and
unrestricted resource use. Full container platforms are sophisticated
systems with many components. This project builds a deliberately small
educational runtime to show how a command can be launched as a child
process with selected Linux isolation and resource controls.

### Proposed solution

A CLI accepts a command and options, validates the configuration,
prepares an isolated child process, applies the supported Linux
namespaces and filesystem setup, optionally applies cgroup resource
limits, executes the command, waits for it, and reports its exit status.
Each kernel feature should be implemented as a small, independently
testable component.

### Core learning outcomes

-   Process creation and lifecycle management with `fork`, `exec`,
    `waitpid`, and signals.
-   Linux namespaces and the isolation they provide.
-   Filesystem roots, mount namespaces, and the limitations of `chroot`.
-   cgroup v2 concepts for CPU and memory controls.
-   Error handling, privilege boundaries, cleanup, and resource
    ownership.
-   CLI design, modular C architecture, integration testing, and
    documentation.

### Intended final demonstration

A reviewer can run a command through the CLI and observe a repeatable,
documented result. The project should demonstrate, where supported by
the test environment:

1.  The requested command starts and its exit code is propagated.
2.  A child process runs with a separate PID namespace and/or hostname
    namespace.
3.  A configured root filesystem is used for filesystem isolation.
4.  CPU and memory limits can be configured through cgroup v2 when
    permissions and the host environment allow it.
5.  Failures caused by unsupported kernel features, missing privileges,
    invalid root filesystems, or unavailable cgroup controllers are
    explained rather than hidden.

### Explicit non-goals

Unless the project owner approves a scope change, do **not** implement:

-   OCI image compatibility or image pulls.
-   Dockerfile builds, registries, layers, or a networked image store.
-   A daemon, REST API, web UI, authentication system, or database.
-   Kubernetes integration or multi-host orchestration.
-   A production security sandbox or a claim of hostile-workload
    isolation.
-   Automatic manipulation of host firewall rules or host-wide kernel
    configuration.
-   Full networking isolation/virtual networking in the first
    deliverable.

------------------------------------------------------------------------

## 3. Recommended Technology Stack

  -------------------------------------------------------------------------------------------
  Area                    Recommendation            Reason
  ----------------------- ------------------------- -----------------------------------------
  Primary language        **C (C11 or later)**      Direct access to Linux/POSIX APIs;
                                                    suitable for an OS course

  Compiler                GCC or Clang              Widely available on Linux

  Build system            **Make**                  Small and transparent for a compact C
                                                    project

  OS APIs                 libc + Linux system calls `fork`, `execvp`, `waitpid`,
                                                    `unshare`/`clone` where appropriate,
                                                    `mount`, `chroot`, `sethostname`, signals

  Isolation               Linux namespaces          Kernel-provided
                                                    process/hostname/mount/IPC/network/user
                                                    isolation

  Resource limits         **cgroup v2**, optional   Modern Linux resource control interface
                          and capability-checked    

  CLI parsing             `getopt_long`             Standard, dependency-light option parsing

  Unit/integration tests  C test executable(s) plus Keeps tests easy to run on a Linux lab
                          shell integration tests   machine

  Static analysis         Compiler warnings;        Catches common mistakes
                          optional                  
                          `clang-tidy`/`cppcheck`   

  Formatting              `clang-format`            Consistent source style

  Documentation           Markdown                  Easy to review and version

  Version control         Git                       Track milestones and changes

  Development environment Native Linux, Linux VM,   Namespace/cgroup support varies by
                          or WSL2 where features    environment
                          work                      
  -------------------------------------------------------------------------------------------

### Compiler baseline

Use strict warnings during development, for example:

``` bash
-Wall -Wextra -Wpedantic -Wshadow -Wconversion -Wformat=2
```

Do not blindly suppress warnings. If a warning is intentionally
unavoidable, document why.

### Dependencies

Keep third-party dependencies minimal. The first version should build
with a standard Linux C toolchain and libc. Do not add a large framework
for functionality already provided by the OS.

------------------------------------------------------------------------

## 4. Architecture

Use a **layered, modular CLI architecture**:

``` text
User
 |
 | mini-docker run [options] -- COMMAND [ARGS...]
 v
CLI / Argument Parser
 |
 v
Configuration Validation
 |
 v
Runtime Orchestrator
 |-------------------------------|
 |               |               |
 v               v               v
Process        Namespace       Resource
Lifecycle      Setup           Controller
 |               |               |
 |               v               v
 |           Filesystem        cgroup v2
 |           / Rootfs          (optional)
 |               |
 |---------------|
         |
         v
   exec target command
         |
         v
 wait / exit status / cleanup
```

### Module responsibilities

-   **CLI:** Parse subcommands and options. Do not perform low-level
    setup directly in the parser.
-   **Config:** Store validated options in a single runtime
    configuration structure.
-   **Runtime:** Orchestrate setup, child creation, synchronization,
    execution, waiting, and cleanup.
-   **Process:** Manage child process creation, signals, waiting, and
    exit-code propagation.
-   **Namespaces:** Request supported namespace isolation and report
    kernel/permission failures.
-   **Filesystem:** Validate rootfs paths and perform mount/root
    switching only when explicitly configured.
-   **Cgroups:** Detect cgroup v2 availability, validate resource
    limits, create/manage only a configured delegated cgroup, write
    limits, and clean up safely.
-   **Logging/errors:** Standardize diagnostics and preserve `errno`
    context.
-   **Tests:** Unit-test pure logic and run integration tests only when
    required kernel capabilities are available.

------------------------------------------------------------------------

## 5. Suggested Repository Structure

Use this structure as the starting point. Agents may make small changes
if there is a clear reason, but must preserve module boundaries and
update this document if the structure materially changes.

``` text
mini-docker/
├── README.md
├── LICENSE
├── Makefile
├── .gitignore
├── .clang-format
├── docs/
│   ├── architecture.md
│   ├── setup-linux.md
│   ├── usage.md
│   ├── security-limitations.md
│   ├── troubleshooting.md
│   └── testing.md
├── include/
│   ├── cli.h
│   ├── config.h
│   ├── error.h
│   ├── log.h
│   ├── process.h
│   ├── runtime.h
│   ├── namespaces.h
│   ├── filesystem.h
│   └── cgroups.h
├── src/
│   ├── main.c
│   ├── cli.c
│   ├── config.c
│   ├── error.c
│   ├── log.c
│   ├── runtime.c
│   ├── process.c
│   ├── namespaces.c
│   ├── filesystem.c
│   └── cgroups.c
├── tests/
│   ├── unit/
│   │   ├── test_config.c
│   │   └── test_cgroups_config.c
│   ├── integration/
│   │   ├── test_run.sh
│   │   ├── test_exit_status.sh
│   │   ├── test_pid_namespace.sh
│   │   ├── test_hostname_namespace.sh
│   │   ├── test_rootfs.sh
│   │   └── test_cgroups.sh
│   └── fixtures/
│       └── README.md
├── scripts/
│   ├── check_environment.sh
│   └── run_tests.sh
├── build/                 # generated; ignored by Git
└── bin/                   # generated binary; ignored by Git
```

### Structure rules

-   Header files declare interfaces; implementations live in `.c` files.
-   Keep `main.c` small: initialize logging, parse arguments, invoke the
    runtime, return the result.
-   Do not place the whole implementation in one file.
-   Do not mix parsing, namespace setup, cgroup writes, and process
    waiting in a single function.
-   Do not commit generated binaries or build output.
-   Do not include real secrets or host-specific absolute paths in
    committed configuration.
-   If optional modules are not implemented yet, keep them clearly
    marked as stubs or defer creating them until the related milestone.

------------------------------------------------------------------------

## 6. CLI Contract

The CLI should be small, predictable, and documented. Proposed command
name: `mini-docker`.

### Initial commands

``` text
mini-docker --help
mini-docker --version
mini-docker check
mini-docker run [OPTIONS] -- COMMAND [ARG...]
```

### Proposed `run` options

``` text
--hostname NAME          Set hostname in a supported UTS namespace
--pid                    Enable PID namespace isolation
--mount                  Enable a mount namespace
--ipc                    Enable IPC namespace isolation
--uts                    Enable UTS namespace isolation
--network                Enable network namespace isolation (advanced/optional)
--rootfs PATH            Use a prepared root filesystem (requires explicit opt-in)
--memory LIMIT           Configure a cgroup v2 memory limit, e.g. 128M
--cpu-quota VALUE        Configure CPU quota using a documented unit
--cgroup-parent PATH     Use an explicitly configured delegated cgroup parent
--keep-rootfs-mounts     Only if a documented use case requires it
-v, --verbose            Print diagnostic setup information
-h, --help               Show help
```

Agents should implement only the options that have working behavior. If
an option is not implemented, either omit it from the accepted CLI or
report it as unsupported; never silently ignore it.

### CLI design decisions

-   Use `--` to separate runtime options from the command being
    executed.
-   Do not pass the command through a shell string. Use `execvp` or an
    equivalent argv-based API to avoid shell injection and quoting bugs.
-   Validate option combinations before changing system state.
-   Make the simplest run mode useful even without a root filesystem,
    while clearly labelling it as partial isolation.
-   `check` should report Linux version/kernel feature availability,
    cgroup v2 presence, effective permissions, and known environment
    limitations. It must not change host configuration.
-   Exit codes: `0` for success; a non-zero status for runtime/setup
    errors; when a child command runs, propagate its exit status where
    practical. Document how signal termination is represented.

### Example command syntax

These are target UX examples, not proof that every option is already
implemented:

``` bash
./bin/mini-docker --help
./bin/mini-docker check
./bin/mini-docker run -- /bin/echo "hello from child"
./bin/mini-docker run --uts --hostname isolated-host -- /bin/hostname
./bin/mini-docker run --pid -- /bin/sh
./bin/mini-docker run --rootfs ./rootfs -- /bin/sh
./bin/mini-docker run --memory 128M -- /usr/bin/sleep 5
```

The exact flag semantics and requirements must be finalized in
`docs/usage.md`. Tests and help text must agree.

------------------------------------------------------------------------

## 7. Runtime Lifecycle

The intended high-level lifecycle is:

1.  Parse CLI arguments.
2.  Validate command, paths, namespace requests, resource values, and
    option combinations.
3.  Run preflight checks for required kernel support and permissions.
4.  Create any required delegated cgroup only if explicitly configured
    and permitted.
5.  Create the child process using a design appropriate for the
    namespaces being requested.
6.  Coordinate parent and child setup with a pipe or another explicit
    synchronization mechanism where ordering matters.
7.  In the child, configure requested namespaces and filesystem state in
    the correct order.
8.  Apply safe process setup; do not assume the process has privileges
    it does not have.
9.  Execute the target with argv-based `exec`.
10. In the parent, wait robustly with `waitpid`, handling `EINTR`.
11. Translate child exit/signal status into a documented result.
12. Remove only resources created by this invocation, after the child
    has exited.
13. Close file descriptors and free allocated memory on all error paths.

### Important implementation detail

Namespace creation, mount setup, cgroup placement, and privilege
dropping have ordering constraints. The runtime must not assume that one
generic sequence works for every combination. Write down the selected
order in `docs/architecture.md`, and test each supported mode. Use
parent/child synchronization when the parent must configure a cgroup
before the child executes.

### Error handling

Every relevant syscall/library operation must be checked, including (as
applicable):

-   `pipe`, `fork`, `clone`/`unshare`
-   `mount`, `umount2`, `chroot`, `chdir`
-   `sethostname`, `setuid`, `setgid`, `setgroups`
-   `open`, `write`, `close`
-   `execvp`, `waitpid`, `kill`
-   cgroup directory and control-file operations

Error messages should include the operation and useful cause,
e.g. `mount namespace setup failed: Operation not permitted`. Do not
expose misleading success output after a setup failure.

------------------------------------------------------------------------

## 8. Linux Concepts and Implementation Requirements

### 8.1 Process management

-   Create and supervise a child process.
-   Execute the target command without constructing a shell command
    string.
-   Wait for the child and propagate its exit status.
-   Handle interrupted waits and child termination by signals.
-   Avoid orphaning children on setup failures.
-   Do not leave temporary cgroups or mount state behind after ordinary
    failures.

### 8.2 Namespaces

Implement incrementally and feature-detect each namespace. Namespace
availability and permissions vary by kernel, distribution, user
namespace configuration, container/VM environment, and security policy.

-   **UTS namespace:** Separate hostname/domain-name view. Useful for a
    visible demo.
-   **PID namespace:** Isolates process IDs visible inside the
    namespace. A process entering a new PID namespace generally needs
    the correct child-creation semantics; merely calling
    `unshare(CLONE_NEWPID)` does not move the calling process into the
    new PID namespace. Verify the first child sees itself as PID 1 where
    this mode is implemented.
-   **Mount namespace:** Separate mount table; pair with deliberate
    mount propagation handling and filesystem setup.
-   **IPC namespace:** Isolates selected System V IPC/POSIX
    message-queue resources.
-   **Network namespace:** Advanced/optional. A new network namespace
    may have no usable network interface by default. Do not claim
    networking works merely because the namespace was created.
-   **User namespace:** Optional advanced work. Mapping IDs and
    capabilities is subtle; do not enable it by default until mappings,
    ownership, and privilege behavior are thoroughly tested.

The CLI should clearly distinguish "namespace requested and successfully
configured" from "not supported in this environment."

### 8.3 Filesystem and rootfs

-   Accept a rootfs only through an explicit `--rootfs` option.
-   Validate the path before any mount/chroot operation; resolve and
    document symlink behavior.
-   Never delete or recursively modify the user-supplied rootfs.
-   A minimal rootfs must contain the requested executable and its
    runtime dependencies. A dynamically linked `/bin/sh` will not work
    if its dynamic loader and shared libraries are absent.
-   Use a mount namespace and appropriate mount setup before changing
    root.
-   Consider mounting `/proc` only when the PID namespace and mount
    setup justify it; mount operations must be explicitly handled and
    cleaned up.
-   Change directory after changing root so the process does not remain
    in the old working directory.
-   Do not claim a secure container based only on `chroot`.
-   Do not automatically download or unpack a rootfs in the first
    version. Document how a developer can prepare a test rootfs safely.

### 8.4 cgroup v2 resource control

-   Detect whether cgroup v2 is mounted and whether the expected
    controllers are available.
-   Use a **delegated cgroup directory** supplied or configured by the
    operator. Do not assume a normal user can write to `/sys/fs/cgroup`.
-   Never change host-wide controller settings automatically.
-   Validate limits before writing them.
-   Support a documented memory limit first; CPU quota can follow.
-   Understand cgroup v2 files such as `memory.max`, `cpu.max`, and
    `cgroup.procs`, subject to controller availability and delegation.
-   Ensure the child is attached to the target cgroup before it executes
    resource-consuming work. Use a synchronization mechanism if needed.
-   Cleanup only the cgroup created by this run and only after it is
    empty.
-   If a controller or permission is missing, return a clear message and
    explain how to run the test in an appropriately configured lab/VM
    environment.

### 8.5 Privileges and security

-   Do not recommend running the whole project with unrestricted root
    privileges as the default development workflow.
-   Some namespace/mount/cgroup demonstrations require privileges or
    delegated capabilities. Explain that in `docs/setup-linux.md`.
-   Never execute untrusted commands or use untrusted rootfs images on a
    personal host as if this were a hardened sandbox.
-   Avoid world-writable temporary directories and predictable temporary
    filenames.
-   Use safe file-descriptor handling, check ownership/permissions where
    relevant, and clean up on failure.
-   Do not disable AppArmor, SELinux, seccomp, or other host security
    controls as an automatic "fix."
-   Document the limitations of the implementation prominently.

------------------------------------------------------------------------

## 9. Configuration and Data Structures

Use a single validated configuration object passed to the runtime. Adapt
names to the code style, but keep the responsibilities clear.

Conceptual example:

``` c
struct runtime_config {
    char **command_argv;
    const char *hostname;
    const char *rootfs_path;
    const char *cgroup_parent;
    unsigned int namespace_flags;
    unsigned long long memory_limit_bytes;
    unsigned long long cpu_quota;
    unsigned long long cpu_period;
    int verbose;
};
```

This is a design sketch, not a requirement to use these exact fields.
Avoid ambiguous ownership of strings: document which module allocates
and frees each field. Prefer explicit units in field names (for example,
`_bytes`, `_usec`) and validate overflow when parsing numeric values.

### Parsing and validation

-   Reject a missing command.
-   Reject malformed limits, negative values, integer overflow, and
    unsupported suffixes.
-   Reject empty or invalid hostnames.
-   Reject incompatible combinations with a useful message.
-   Never interpret user-provided strings as shell source.
-   Ensure parsed options remain valid for the duration of the child
    launch.

------------------------------------------------------------------------

## 10. Logging and Error Conventions

Provide concise default output and more detailed output under
`--verbose`.

Suggested conventions:

-   Normal success: print little or nothing beyond the child command's
    own output.
-   Verbose mode: report requested namespaces, selected rootfs, cgroup
    configuration, and cleanup steps.
-   Errors: write diagnostics to stderr.
-   Include the failed operation and relevant `errno` message.
-   Do not print credentials, sensitive environment values, or
    unnecessary host information.
-   Avoid a large logging framework; a few small functions are enough.

Suggested API (adapt as needed):

``` c
void log_info(const char *fmt, ...);
void log_debug(const char *fmt, ...);
void log_error(const char *fmt, ...);
```

Use a consistent error-return convention across modules. Document when a
function returns `-1` and sets `errno`, or returns a project-specific
error code.

------------------------------------------------------------------------

## 11. Build and Developer Workflow

### Expected commands

``` bash
make
make test
make test-unit
make test-integration
make clean
./bin/mini-docker --help
./bin/mini-docker check
```

The Makefile may use slightly different target names, but `README.md`
must document the actual commands.

### Build requirements

-   Compile into `build/` and place the final executable at
    `bin/mini-docker`.
-   Use header dependencies so changing a header triggers recompilation.
-   Fail the build when compilation fails.
-   Keep compiler warnings enabled.
-   `make clean` must remove only generated project artifacts.
-   The build should not need network access.
-   Unit tests should not require root.
-   Privilege-dependent integration tests must detect unavailable
    capabilities and report **SKIP**, not a false failure or false pass.

### Environment check

`scripts/check_environment.sh` and/or `mini-docker check` should report:

-   OS/kernel information relevant to the runtime.
-   Compiler/build tools.
-   Namespace capability/probe results where safe.
-   cgroup v2 mount and controller availability.
-   Whether required paths are writable by the current user.
-   Common restrictions in containers, VMs, or WSL2.

The check must be read-only and must not try to "fix" the host.

------------------------------------------------------------------------

## 12. Testing Plan and Acceptance Criteria

Tests should focus on observable behavior and cleanup, not only on
internal helper functions.

### Unit tests

-   CLI rejects a missing command.
-   CLI accepts `--` and preserves command arguments correctly.
-   Memory-size parser accepts documented forms (e.g. `128M`) and
    rejects malformed or overflowing values.
-   CPU limit parser rejects invalid ranges.
-   Hostname and path validation behave as documented.
-   Option-combination validation rejects unsupported combinations.
-   Error formatting includes the failed operation.

### Basic integration tests

1.  **Help/version:** return success and print expected usage/version.
2.  **Simple execution:** running `/bin/echo hello` prints `hello`.
3.  **Argument preservation:** arguments containing spaces are passed as
    single arguments.
4.  **Exit status:** a child exiting with a known non-zero status is
    reflected by the runtime.
5.  **Missing executable:** report an actionable error and clean up.
6.  **Signal handling:** interrupt/terminate a test child and verify the
    parent does not hang or leave a child behind.
7.  **Repeated runs:** several sequential runs do not leak file
    descriptors, temporary directories, or cgroups.

### Feature integration tests (capability-dependent)

-   **UTS:** hostname differs inside the namespace and the host hostname
    remains unchanged.
-   **PID:** the process sees the expected PID namespace behavior;
    verify PID 1 semantics when claimed.
-   **Mount/rootfs:** the child sees the intended filesystem root; host
    mounts and files remain unchanged after exit.
-   **cgroups:** the child is attached before execution; configured
    limits are visible and the created cgroup is removed after exit.
-   **Failure paths:** denied namespace creation, invalid rootfs,
    unavailable cgroup controller, and unwritable delegated cgroup
    produce a clear error and clean up partial setup.

### Test reporting

-   Separate required baseline tests from environment-dependent tests.
-   A skipped privileged test must state why it was skipped.
-   Do not treat "operation not permitted" as proof the feature works.
-   Record the test environment and command used when documenting
    results.
-   Never claim full test coverage without evidence.

### Definition of done for a feature

A feature is complete only when:

1.  The implementation exists and compiles with the configured warnings.
2.  The CLI/help/documentation describe its actual behavior.
3.  There is at least one successful test where the environment supports
    it.
4.  Failure behavior is tested.
5.  Resources are cleaned up on both success and failure.
6.  Security limitations are documented.
7.  The feature does not break the baseline CLI tests.

------------------------------------------------------------------------

## 13. Implementation Milestones

Work in this order. Do not start all kernel features at once.

### Milestone 0 --- Repository and build skeleton

-   Create the repository layout.
-   Add Makefile, headers, logging/error helpers, and a minimal
    executable.
-   Add `--help`, `--version`, and a read-only `check` command.
-   Add basic unit-test wiring and `.gitignore`.
-   **Exit criterion:** clean build; help/version/check work; no runtime
    isolation claims yet.

### Milestone 1 --- Command execution and process lifecycle

-   Implement `run -- COMMAND ARGS...`.
-   Use argv-based execution.
-   Wait for the child, propagate status, handle `EINTR`, and clean up.
-   Add tests for arguments, missing executable, exit status, and
    signals.
-   **Exit criterion:** reliable unisolated command execution with
    documented behavior.

### Milestone 2 --- Namespace foundation

-   Add UTS namespace/hostname behavior first because it is easy to
    demonstrate.
-   Add PID namespace with correct child-creation semantics and tests.
-   Add mount namespace and IPC namespace behind explicit flags.
-   Add preflight diagnostics and environment-dependent skips.
-   **Exit criterion:** each enabled namespace has a test demonstrating
    its behavior and limitations.

### Milestone 3 --- Root filesystem support

-   Add explicit rootfs validation.
-   Implement mount/root-switch workflow in the correct namespace.
-   Handle working directory and required mounts deliberately.
-   Document preparation of a minimal rootfs and dynamic executable
    dependencies.
-   Add tests that verify isolation and cleanup.
-   **Exit criterion:** a command can run against a prepared rootfs in a
    supported Linux environment without modifying the host rootfs.

### Milestone 4 --- cgroup v2 memory limits

-   Detect cgroup v2 and memory controller/delegation.
-   Parse and validate memory limits.
-   Create a child cgroup only inside an explicitly configured delegated
    parent.
-   Ensure child placement precedes target execution.
-   Clean up the cgroup on normal and error paths.
-   **Exit criterion:** successful limit configuration in a supported
    environment and clean skips/errors elsewhere.

### Milestone 5 --- CPU limits and robustness

-   Add CPU quota/period configuration with clear units.
-   Improve signal forwarding and termination cleanup.
-   Test partial-setup failures and repeated runs.
-   **Exit criterion:** CPU limits work where supported; lifecycle
    behavior remains stable.

### Milestone 6 --- Documentation and demonstration readiness

-   Finalize architecture, setup, usage, security limitations,
    troubleshooting, and testing docs.
-   Add a short repeatable demo script that never changes host
    configuration automatically.
-   Run the full available test suite and record results honestly.
-   **Exit criterion:** a reviewer can clone, build, check the
    environment, run baseline demos, and understand which optional
    features require extra permissions.

------------------------------------------------------------------------

## 14. Documentation Requirements

### `README.md`

Must include:

-   What the project does and does not do.
-   Linux-only status and prerequisites.
-   Build commands.
-   Quick-start commands.
-   Feature support matrix.
-   Test commands.
-   Known limitations and security warning.
-   Current implementation status.

### `docs/architecture.md`

Must include:

-   Module responsibilities.
-   Process/runtime lifecycle.
-   Parent-child synchronization points.
-   Namespace and mount ordering decisions.
-   cgroup placement and cleanup flow.
-   Error and exit-status behavior.

### `docs/setup-linux.md`

Must include:

-   Supported development environment.
-   Compiler/build prerequisites.
-   Kernel and cgroup assumptions.
-   Permission/delegation requirements.
-   How to run unprivileged baseline tests.
-   How to run privileged tests in a disposable Linux VM/lab setup.
-   No automatic host reconfiguration.

### `docs/usage.md`

Must include actual implemented commands and option semantics, with
examples and expected results. Never list a planned option as working.

### `docs/security-limitations.md`

Must state plainly:

-   This is educational, not a hardened sandbox.
-   `chroot` alone is not a security boundary.
-   Root/capabilities and host kernel configuration affect isolation.
-   No OCI compatibility or production-grade threat model is promised.
-   Untrusted workloads and root filesystems should not be run on a
    personal host under the assumption that they are safely contained.

### `docs/testing.md`

Must describe test categories, prerequisites, exact commands, skip
behavior, and the last verified test results.

------------------------------------------------------------------------

## 15. Coding Style and Quality Bar

-   Use descriptive function and variable names.
-   Keep functions focused; avoid giant orchestration functions.
-   Use `const` where appropriate.
-   Check all allocations and system calls.
-   Close file descriptors exactly once; initialize descriptor variables
    to safe sentinel values.
-   Avoid global mutable state.
-   Use `size_t` and fixed-width types where appropriate.
-   Check integer parsing for errors and overflow.
-   Do not silently ignore failed cleanup operations; log them when
    useful.
-   Keep cleanup paths explicit and idempotent where practical.
-   Comment on **why** kernel-specific ordering is necessary, not every
    obvious line.
-   No fake implementations, hard-coded "success" output, or untested
    stubs presented as complete.
-   Do not add frameworks/dependencies without explaining the benefit.

------------------------------------------------------------------------

## 16. Suggested Agent Workflow

If multiple coding agents are used, assign work by module and milestone:

-   **Agent A --- CLI/config:** argument parsing, validation,
    help/version, configuration tests.
-   **Agent B --- Process lifecycle:** child execution,
    wait/status/signal behavior, baseline integration tests.
-   **Agent C --- Namespace implementation:** implement only after the
    process-lifecycle interface is agreed; add capability-aware tests.
-   **Agent D --- Filesystem/cgroups:** work behind stable interfaces;
    do not change host configuration; add explicit failure/cleanup
    tests.
-   **Integrator/reviewer:** own the Makefile, module contracts,
    integration, security review, docs, and end-to-end acceptance.

Agents must agree on public header interfaces before parallel
implementation. Do not allow agents to independently invent incompatible
configuration structures or error conventions. Merge one milestone at a
time and run the full baseline suite after every integration.

### Required handoff from each agent

Each agent should report:

1.  Files created/modified.
2.  Feature behavior implemented.
3.  Build/test commands executed.
4.  Actual test results, including skipped tests and reasons.
5.  Known limitations and follow-up work.
6.  Any public interface or architecture changes.

------------------------------------------------------------------------

## 17. Definition of Project Completion

The project is ready for final academic demonstration when:

-   [ ] A fresh checkout builds using documented commands on a supported
    Linux environment.
-   [ ] The CLI has help, version, environment check, and reliable
    command execution.
-   [ ] Child exit status and common failure paths are handled
    correctly.
-   [ ] Each claimed namespace behavior is demonstrated by a test.
-   [ ] Rootfs support is tested in a suitable environment, if included
    in the final claim.
-   [ ] cgroup v2 limits are tested where delegation and controllers are
    available, if included in the final claim.
-   [ ] Partial setup is cleaned up without damaging host resources.
-   [ ] No host-wide configuration is changed automatically.
-   [ ] The README and docs accurately separate supported features from
    planned features.
-   [ ] Security limitations are prominent and honest.
-   [ ] The demo is repeatable and its prerequisites are documented.
-   [ ] No feature is marked complete solely because code compiles.

------------------------------------------------------------------------

## 18. Reference Material

Use authoritative Linux documentation as the technical reference:

-   Linux man-pages: `fork(2)`, `execve(2)`, `waitpid(2)`, `clone(2)`,
    `unshare(2)`, `namespaces(7)`, `pid_namespaces(7)`, `mount(2)`,
    `chroot(2)`, `cgroups(7)`.
-   Kernel documentation for cgroup v2 and namespaces.
-   *Operating System Concepts* by Silberschatz, Galvin, and Gagne for
    course-level process and OS concepts.

When implementation behavior depends on kernel version or distribution
configuration, verify the actual environment instead of assuming a
feature is available.

------------------------------------------------------------------------

## 19. Final Instructions to the Coding Agent

Start by inspecting the existing repository before creating or
overwriting files. Preserve any working code and identify the current
state. Then implement **Milestone 0 and Milestone 1 first**, run the
tests, and report the results. Continue milestone-by-milestone. Do not
attempt a giant one-shot implementation of all isolation features.

If the repository already contains code, adapt this architecture to it
rather than blindly replacing it. If a requirement is blocked by kernel
support or privileges, document the blocker and implement a clear
preflight error or test skip; do not fake the feature.

**The target is a small, understandable, testable educational container
runtime---not a production Docker clone.**
