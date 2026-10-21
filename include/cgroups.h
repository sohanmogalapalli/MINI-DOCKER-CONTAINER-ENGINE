#ifndef MINI_DOCKER_CGROUPS_H
#define MINI_DOCKER_CGROUPS_H

#include "config.h"
#include "error.h"
#include <sys/types.h>
#include <stdbool.h>

typedef struct {
    bool cgroup2_mounted;
    bool has_memory;
    bool has_cpu;
    bool has_pids;
    char root_path[256];
} cgroup_support_t;

typedef struct {
    char cgroup_path[512];
    bool active;
} cgroup_ctx_t;

void cgroups_probe_support(cgroup_support_t *support);
md_error_t cgroups_init_context(const runtime_config_t *cfg, pid_t child_pid, cgroup_ctx_t *ctx);
md_error_t cgroups_apply_limits(const runtime_config_t *cfg, const cgroup_ctx_t *ctx);
md_error_t cgroups_attach_pid(const cgroup_ctx_t *ctx, pid_t pid);
md_error_t cgroups_cleanup(cgroup_ctx_t *ctx);

#endif /* MINI_DOCKER_CGROUPS_H */
