#include "config.h"
#include "log.h"
#include <ctype.h>
#include <errno.h>
#include <inttypes.h>
#include <limits.h>
#include <stdlib.h>
#include <string.h>

void config_init(runtime_config_t *cfg) {
    if (!cfg) return;
    cfg->command_argv = NULL;
    cfg->command_argc = 0;
    cfg->hostname = NULL;
    cfg->rootfs_path = NULL;
    cfg->cgroup_parent = strdup("/sys/fs/cgroup/mini-docker");
    cfg->ns_flags = 0;
    cfg->memory_limit_bytes = 0;
    cfg->cpu_quota_us = 0;
    cfg->cpu_period_us = 100000; /* Default 100ms in Linux CFS */
    cfg->verbose = false;
    cfg->check_only = false;
}

void config_free(runtime_config_t *cfg) {
    if (!cfg) return;
    if (cfg->hostname) {
        free(cfg->hostname);
        cfg->hostname = NULL;
    }
    if (cfg->rootfs_path) {
        free(cfg->rootfs_path);
        cfg->rootfs_path = NULL;
    }
    if (cfg->cgroup_parent) {
        free(cfg->cgroup_parent);
        cfg->cgroup_parent = NULL;
    }
    /* Note: command_argv pointers point to argv array passed to main */
    cfg->command_argv = NULL;
    cfg->command_argc = 0;
}

md_error_t config_parse_memory(const char *str, uint64_t *out_bytes) {
    if (!str || !out_bytes || *str == '\0') {
        return MD_ERR_INVALID_ARGS;
    }

    /* Check for negative sign or non-digits at start */
    if (*str == '-' || !isdigit((unsigned char)*str)) {
        return MD_ERR_INVALID_ARGS;
    }

    char *endptr = NULL;
    errno = 0;
    unsigned long long val = strtoull(str, &endptr, 10);
    if (errno == ERANGE || val == ULLONG_MAX) {
        return MD_ERR_INVALID_ARGS;
    }

    uint64_t multiplier = 1;
    if (endptr && *endptr != '\0') {
        /* Skip optional spaces */
        while (*endptr == ' ') endptr++;
        char unit = (char)toupper((unsigned char)*endptr);
        endptr++;
        if (*endptr == 'B' || *endptr == 'b') {
            endptr++;
        }
        while (*endptr == ' ') endptr++;
        if (*endptr != '\0') {
            return MD_ERR_INVALID_ARGS; /* Extra characters */
        }

        switch (unit) {
            case 'K':
                multiplier = 1024ULL;
                break;
            case 'M':
                multiplier = 1024ULL * 1024ULL;
                break;
            case 'G':
                multiplier = 1024ULL * 1024ULL * 1024ULL;
                break;
            case 'B':
                multiplier = 1;
                break;
            default:
                return MD_ERR_INVALID_ARGS;
        }
    }

    /* Check overflow */
    if (val > (UINT64_MAX / multiplier)) {
        return MD_ERR_INVALID_ARGS;
    }

    *out_bytes = (uint64_t)(val * multiplier);
    return MD_SUCCESS;
}

md_error_t config_parse_cpu(const char *str, uint64_t *out_quota, uint64_t *out_period) {
    if (!str || !out_quota || !out_period || *str == '\0') {
        return MD_ERR_INVALID_ARGS;
    }

    if (*str == '-' || !isdigit((unsigned char)*str)) {
        return MD_ERR_INVALID_ARGS;
    }

    char *endptr = NULL;
    errno = 0;
    unsigned long long quota = strtoull(str, &endptr, 10);
    if (errno == ERANGE || quota == 0) {
        return MD_ERR_INVALID_ARGS;
    }

    unsigned long long period = 100000; /* Default 100ms */

    if (endptr && (*endptr == '/' || *endptr == ' ' || *endptr == ':')) {
        endptr++;
        while (*endptr == ' ') endptr++;
        if (isdigit((unsigned char)*endptr)) {
            errno = 0;
            period = strtoull(endptr, &endptr, 10);
            if (errno == ERANGE || period == 0) {
                return MD_ERR_INVALID_ARGS;
            }
        }
    }

    while (endptr && *endptr == ' ') endptr++;
    if (endptr && *endptr != '\0') {
        return MD_ERR_INVALID_ARGS;
    }

    *out_quota = (uint64_t)quota;
    *out_period = (uint64_t)period;
    return MD_SUCCESS;
}

md_error_t config_validate(const runtime_config_t *cfg) {
    if (!cfg) return MD_ERR_INVALID_ARGS;

    if (cfg->check_only) {
        return MD_SUCCESS;
    }

    if (!cfg->command_argv || cfg->command_argc == 0 || !cfg->command_argv[0]) {
        log_error("No command specified. Use '-- COMMAND [ARGS...]'");
        return MD_ERR_CONFIG;
    }

    if (cfg->hostname) {
        size_t len = strlen(cfg->hostname);
        if (len == 0 || len > 64) {
            log_error("Invalid hostname length (must be 1-64 characters): '%s'", cfg->hostname);
            return MD_ERR_CONFIG;
        }
        for (size_t i = 0; i < len; i++) {
            char c = cfg->hostname[i];
            if (!isalnum((unsigned char)c) && c != '-' && c != '.') {
                log_error("Invalid character '%c' in hostname", c);
                return MD_ERR_CONFIG;
            }
        }
    }

    if (cfg->rootfs_path) {
        if (strlen(cfg->rootfs_path) == 0) {
            log_error("Rootfs path cannot be empty");
            return MD_ERR_CONFIG;
        }
    }

    return MD_SUCCESS;
}
