#include "cgroups.h"
#include "log.h"
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

static int write_cgroup_file(const char *path, const char *value) {
    int fd = open(path, O_WRONLY | O_CLOEXEC);
    if (fd < 0) {
        return -1;
    }
    size_t len = strlen(value);
    ssize_t written = write(fd, value, len);
    close(fd);
    if (written < 0 || (size_t)written != len) {
        return -1;
    }
    return 0;
}

void cgroups_probe_support(cgroup_support_t *support) {
    if (!support) return;
    memset(support, 0, sizeof(*support));
    strncpy(support->root_path, "/sys/fs/cgroup", sizeof(support->root_path) - 1);

    char controllers_path[512];
    snprintf(controllers_path, sizeof(controllers_path), "%s/cgroup.controllers", support->root_path);

    FILE *f = fopen(controllers_path, "r");
    if (!f) {
        support->cgroup2_mounted = false;
        return;
    }

    support->cgroup2_mounted = true;
    char line[256];
    if (fgets(line, sizeof(line), f)) {
        if (strstr(line, "memory")) support->has_memory = true;
        if (strstr(line, "cpu")) support->has_cpu = true;
        if (strstr(line, "pids")) support->has_pids = true;
    }
    fclose(f);
}

md_error_t cgroups_init_context(const runtime_config_t *cfg, pid_t child_pid, cgroup_ctx_t *ctx) {
    if (!cfg || !ctx) return MD_ERR_INVALID_ARGS;
    memset(ctx, 0, sizeof(*ctx));

    /* Only initialize if memory or cpu limits were requested */
    if (cfg->memory_limit_bytes == 0 && cfg->cpu_quota_us == 0) {
        return MD_SUCCESS;
    }

    const char *parent = cfg->cgroup_parent ? cfg->cgroup_parent : "/sys/fs/cgroup/mini-docker";

    /* Ensure parent cgroup directory exists */
    struct stat st;
    if (stat(parent, &st) != 0) {
        if (mkdir(parent, 0755) != 0) {
            md_perror("mkdir cgroup parent", errno);
            log_error("Failed to create cgroup parent at %s. Privilege or delegation required.", parent);
            return MD_ERR_CGROUPS;
        }
    }

    /* Enable controllers in parent subtree_control if possible */
    char subtree_path[600];
    snprintf(subtree_path, sizeof(subtree_path), "%s/cgroup.subtree_control", parent);
    write_cgroup_file(subtree_path, "+memory +cpu");

    /* Create unique child cgroup directory for this container run */
    snprintf(ctx->cgroup_path, sizeof(ctx->cgroup_path), "%s/container-%d", parent, (int)child_pid);
    if (mkdir(ctx->cgroup_path, 0755) != 0) {
        if (errno != EEXIST) {
            md_perror("mkdir container cgroup", errno);
            return MD_ERR_CGROUPS;
        }
    }
    ctx->active = true;
    log_debug("Created cgroup v2 container directory: %s", ctx->cgroup_path);

    return MD_SUCCESS;
}

md_error_t cgroups_apply_limits(const runtime_config_t *cfg, const cgroup_ctx_t *ctx) {
    if (!ctx || !ctx->active) {
        return MD_SUCCESS;
    }

    char file_path[600];
    char value_buf[64];

    /* Apply memory limit */
    if (cfg->memory_limit_bytes > 0) {
        snprintf(file_path, sizeof(file_path), "%s/memory.max", ctx->cgroup_path);
        snprintf(value_buf, sizeof(value_buf), "%" PRIu64 "\n", cfg->memory_limit_bytes);
        log_debug("Setting memory.max to %s in %s", value_buf, file_path);
        if (write_cgroup_file(file_path, value_buf) != 0) {
            md_perror("write memory.max", errno);
            return MD_ERR_CGROUPS;
        }
    }

    /* Apply CPU quota / period */
    if (cfg->cpu_quota_us > 0) {
        snprintf(file_path, sizeof(file_path), "%s/cpu.max", ctx->cgroup_path);
        snprintf(value_buf, sizeof(value_buf), "%" PRIu64 " %" PRIu64 "\n", cfg->cpu_quota_us, cfg->cpu_period_us);
        log_debug("Setting cpu.max to %s in %s", value_buf, file_path);
        if (write_cgroup_file(file_path, value_buf) != 0) {
            md_perror("write cpu.max", errno);
            return MD_ERR_CGROUPS;
        }
    }

    return MD_SUCCESS;
}

md_error_t cgroups_attach_pid(const cgroup_ctx_t *ctx, pid_t pid) {
    if (!ctx || !ctx->active) {
        return MD_SUCCESS;
    }

    char procs_path[600];
    char pid_str[32];
    snprintf(procs_path, sizeof(procs_path), "%s/cgroup.procs", ctx->cgroup_path);
    snprintf(pid_str, sizeof(pid_str), "%d\n", (int)pid);

    log_debug("Attaching PID %d to cgroup: %s", (int)pid, procs_path);
    if (write_cgroup_file(procs_path, pid_str) != 0) {
        md_perror("write cgroup.procs", errno);
        return MD_ERR_CGROUPS;
    }

    return MD_SUCCESS;
}

md_error_t cgroups_cleanup(cgroup_ctx_t *ctx) {
    if (!ctx || !ctx->active) {
        return MD_SUCCESS;
    }

    log_debug("Cleaning up cgroup directory: %s", ctx->cgroup_path);

    /* Try multiple times if kernel is still draining processes */
    int retries = 5;
    while (retries-- > 0) {
        if (rmdir(ctx->cgroup_path) == 0) {
            ctx->active = false;
            return MD_SUCCESS;
        }
        if (errno == EBUSY) {
            usleep(20000); /* 20ms */
            continue;
        }
        break;
    }

    if (ctx->active) {
        md_perror("rmdir cgroup_path", errno);
        log_warn("Failed to remove cgroup directory %s (may still contain processes)", ctx->cgroup_path);
        return MD_ERR_CGROUPS;
    }

    return MD_SUCCESS;
}
