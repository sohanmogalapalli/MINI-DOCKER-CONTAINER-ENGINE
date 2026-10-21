#ifndef MINI_DOCKER_NAMESPACES_H
#define MINI_DOCKER_NAMESPACES_H

#include "config.h"
#include "error.h"
#include <stdbool.h>

typedef struct {
    bool has_uts;
    bool has_pid;
    bool has_mount;
    bool has_ipc;
    bool has_net;
    bool has_user;
} ns_support_t;

void namespaces_probe_support(ns_support_t *support);
md_error_t namespaces_apply_prefork(const runtime_config_t *cfg);
md_error_t namespaces_apply_postfork_child(const runtime_config_t *cfg);

#endif /* MINI_DOCKER_NAMESPACES_H */
