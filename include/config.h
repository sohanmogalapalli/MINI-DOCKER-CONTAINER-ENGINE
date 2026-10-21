#ifndef MINI_DOCKER_CONFIG_H
#define MINI_DOCKER_CONFIG_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "error.h"

#define MD_NS_UTS     (1U << 0)
#define MD_NS_PID     (1U << 1)
#define MD_NS_MOUNT   (1U << 2)
#define MD_NS_IPC     (1U << 3)
#define MD_NS_NET     (1U << 4)

typedef struct {
    char **command_argv;       /* Command and arguments to execute (NULL terminated) */
    int command_argc;          /* Count of command arguments */
    char *hostname;            /* Desired container hostname (or NULL) */
    char *rootfs_path;         /* Absolute or validated path to rootfs (or NULL) */
    char *cgroup_parent;       /* Cgroup v2 parent directory (default: /sys/fs/cgroup/mini-docker) */
    uint32_t ns_flags;         /* Bitmask of MD_NS_* flags */
    uint64_t memory_limit_bytes;/* 0 means no limit */
    uint64_t cpu_quota_us;     /* CPU quota in microseconds per period (0 = none) */
    uint64_t cpu_period_us;    /* CPU period in microseconds (default 100000 = 100ms) */
    bool verbose;              /* Verbose output */
    bool check_only;           /* Run environment checks only */
} runtime_config_t;

void config_init(runtime_config_t *cfg);
void config_free(runtime_config_t *cfg);
md_error_t config_parse_memory(const char *str, uint64_t *out_bytes);
md_error_t config_parse_cpu(const char *str, uint64_t *out_quota, uint64_t *out_period);
md_error_t config_validate(const runtime_config_t *cfg);

#endif /* MINI_DOCKER_CONFIG_H */
