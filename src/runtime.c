#include "runtime.h"
#include "cgroups.h"
#include "error.h"
#include "filesystem.h"
#include "log.h"
#include "namespaces.h"
#include "process.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/utsname.h>
#include <sys/wait.h>
#include <unistd.h>

int runtime_check_environment(void) {
    printf("=== Mini Docker Container Engine - Environment Preflight Check ===\n\n");

    /* 1. Host Kernel Information */
    struct utsname uts;
    if (uname(&uts) == 0) {
        printf("[+] Operating System  : %s %s\n", uts.sysname, uts.release);
        printf("[+] Host Architecture : %s\n", uts.machine);
        printf("[+] Host Node Name    : %s\n", uts.nodename);
    } else {
        printf("[-] Failed to query host kernel via uname(2)\n");
    }

    /* 2. Effective Privileges */
    uid_t uid = getuid();
    uid_t euid = geteuid();
    printf("[+] Effective UID/GID : UID=%d (EUID=%d), GID=%d\n", (int)uid, (int)euid, (int)getgid());
    if (euid == 0) {
        printf("[+] Privilege Level   : Superuser / Root (Full capabilities available)\n");
    } else {
        printf("[!] Privilege Level   : Unprivileged User (Namespace/mount may require sudo or user namespaces)\n");
    }

    /* 3. Linux Namespaces */
    printf("\n--- Linux Namespace Support (/proc/self/ns) ---\n");
    ns_support_t ns;
    namespaces_probe_support(&ns);
    printf("  UTS Namespace    : %s\n", ns.has_uts ? "YES (Supported)" : "NO");
    printf("  PID Namespace    : %s\n", ns.has_pid ? "YES (Supported)" : "NO");
    printf("  Mount Namespace  : %s\n", ns.has_mount ? "YES (Supported)" : "NO");
    printf("  IPC Namespace    : %s\n", ns.has_ipc ? "YES (Supported)" : "NO");
    printf("  Net Namespace    : %s\n", ns.has_net ? "YES (Supported)" : "NO");
    printf("  User Namespace   : %s\n", ns.has_user ? "YES (Supported)" : "NO");

    /* 4. cgroup v2 Resource Control */
    printf("\n--- cgroup v2 Resource Control ---\n");
    cgroup_support_t cg;
    cgroups_probe_support(&cg);
    if (cg.cgroup2_mounted) {
        printf("[+] cgroup v2 Unified : YES (Mounted at %s)\n", cg.root_path);
        printf("  Memory Controller: %s\n", cg.has_memory ? "YES (Available)" : "NO");
        printf("  CPU Controller   : %s\n", cg.has_cpu ? "YES (Available)" : "NO");
        printf("  PIDs Controller  : %s\n", cg.has_pids ? "YES (Available)" : "NO");

        /* Check writable access */
        if (access(cg.root_path, W_OK) == 0) {
            printf("[+] cgroup Write Access: Granted (Directly writable)\n");
        } else {
            printf("[!] cgroup Write Access: Read-only (Delegated path or sudo required for limits)\n");
        }
    } else {
        printf("[-] cgroup v2 Unified : NOT MOUNTED (cgroup limits unavailable)\n");
    }

    printf("\n=== Preflight Check Completed ===\n");
    return 0;
}

static int run_with_pid_ns(const runtime_config_t *cfg, process_sync_t *sync, cgroup_ctx_t *cg_ctx) {
    /* 1. Parent forks Child 1 */
    pid_t child1 = fork();
    if (child1 < 0) {
        md_perror("fork child1", errno);
        return MD_ERR_SYSCALL;
    }

    if (child1 == 0) {
        /* Child 1: Unshare PID and other namespaces */
        process_sync_init_in_child(sync);

        md_error_t ns_err = namespaces_apply_postfork_child(cfg);
        if (ns_err != MD_SUCCESS) {
            process_sync_destroy(sync);
            exit(MD_ERR_NAMESPACE);
        }

        /* Fork Child 2 (this child enters the new PID namespace as PID 1) */
        pid_t child2 = fork();
        if (child2 < 0) {
            md_perror("fork child2", errno);
            process_sync_destroy(sync);
            exit(MD_ERR_SYSCALL);
        }

        if (child2 == 0) {
            /* Child 2 (PID 1 inside container) */
            log_debug("Inside PID namespace: getpid() = %d", (int)getpid());

            /* Sync with parent so cgroup limits can be applied to child1/child2 */
            if (cfg->memory_limit_bytes > 0 || cfg->cpu_quota_us > 0) {
                if (process_sync_wait_for_parent(sync) != MD_SUCCESS) {
                    process_sync_destroy(sync);
                    exit(MD_ERR_SYSCALL);
                }
            }

            /* Filesystem isolation */
            if (cfg->rootfs_path) {
                if (fs_setup_rootfs(cfg) != MD_SUCCESS) {
                    process_sync_destroy(sync);
                    exit(MD_ERR_FILESYSTEM);
                }
            }

            process_sync_destroy(sync);

            /* Execute target command */
            process_exec(cfg);
            exit(MD_ERR_EXEC);
        }

        /* Child 1 in host namespace */
        log_debug("Child 1 spawned Container PID 1 (Host PID=%d)", (int)child2);

        /* Child 1 waits for Child 2 (the container) */
        int status = 0;
        waitpid(child2, &status, 0);
        process_sync_destroy(sync);
        if (WIFEXITED(status)) {
            exit(WEXITSTATUS(status));
        } else if (WIFSIGNALED(status)) {
            exit(128 + WTERMSIG(status));
        }
        exit(1);
    }

    /* Parent Process */
    process_sync_init_in_parent(sync);

    /* Setup cgroups on child1 */
    if (cfg->memory_limit_bytes > 0 || cfg->cpu_quota_us > 0) {
        if (cgroups_init_context(cfg, child1, cg_ctx) == MD_SUCCESS) {
            cgroups_apply_limits(cfg, cg_ctx);
            cgroups_attach_pid(cg_ctx, child1);
        }
        process_sync_notify_child(sync);
    }

    int exit_code = process_wait(child1);
    process_sync_destroy(sync);
    cgroups_cleanup(cg_ctx);
    return exit_code;
}

static int run_direct(const runtime_config_t *cfg, process_sync_t *sync, cgroup_ctx_t *cg_ctx) {
    pid_t child = fork();
    if (child < 0) {
        md_perror("fork", errno);
        return MD_ERR_SYSCALL;
    }

    if (child == 0) {
        /* Child process */
        process_sync_init_in_child(sync);

        /* Apply namespaces */
        if (namespaces_apply_postfork_child(cfg) != MD_SUCCESS) {
            process_sync_destroy(sync);
            exit(MD_ERR_NAMESPACE);
        }

        /* Sync with parent if cgroups requested */
        if (cfg->memory_limit_bytes > 0 || cfg->cpu_quota_us > 0) {
            if (process_sync_wait_for_parent(sync) != MD_SUCCESS) {
                process_sync_destroy(sync);
                exit(MD_ERR_SYSCALL);
            }
        }

        /* Filesystem / rootfs setup */
        if (cfg->rootfs_path) {
            if (fs_setup_rootfs(cfg) != MD_SUCCESS) {
                process_sync_destroy(sync);
                exit(MD_ERR_FILESYSTEM);
            }
        }

        process_sync_destroy(sync);

        /* Execute command */
        process_exec(cfg);
        exit(MD_ERR_EXEC);
    }

    /* Parent process */
    process_sync_init_in_parent(sync);

    if (cfg->memory_limit_bytes > 0 || cfg->cpu_quota_us > 0) {
        if (cgroups_init_context(cfg, child, cg_ctx) == MD_SUCCESS) {
            cgroups_apply_limits(cfg, cg_ctx);
            cgroups_attach_pid(cg_ctx, child);
        }
        process_sync_notify_child(sync);
    }

    int exit_code = process_wait(child);
    process_sync_destroy(sync);
    cgroups_cleanup(cg_ctx);
    return exit_code;
}

int runtime_run(const runtime_config_t *cfg) {
    if (!cfg) return MD_ERR_INVALID_ARGS;

    if (cfg->check_only) {
        return runtime_check_environment();
    }

    /* Validate rootfs path if specified */
    if (cfg->rootfs_path) {
        md_error_t err = fs_validate_rootfs(cfg->rootfs_path);
        if (err != MD_SUCCESS) {
            return (int)err;
        }
    }

    log_debug("Starting container runtime orchestrator");

    process_sync_t sync;
    if (process_sync_init(&sync) != MD_SUCCESS) {
        return MD_ERR_SYSCALL;
    }

    cgroup_ctx_t cg_ctx;
    memset(&cg_ctx, 0, sizeof(cg_ctx));

    int result = 0;
    if (cfg->ns_flags & MD_NS_PID) {
        result = run_with_pid_ns(cfg, &sync, &cg_ctx);
    } else {
        result = run_direct(cfg, &sync, &cg_ctx);
    }

    return result;
}
