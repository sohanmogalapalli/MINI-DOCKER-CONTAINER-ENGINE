#include "namespaces.h"
#include "log.h"
#include <errno.h>
#include <fcntl.h>
#include <sched.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>

void namespaces_probe_support(ns_support_t *support) {
    if (!support) return;
    support->has_uts = (access("/proc/self/ns/uts", F_OK) == 0);
    support->has_pid = (access("/proc/self/ns/pid", F_OK) == 0);
    support->has_mount = (access("/proc/self/ns/mnt", F_OK) == 0);
    support->has_ipc = (access("/proc/self/ns/ipc", F_OK) == 0);
    support->has_net = (access("/proc/self/ns/net", F_OK) == 0);
    support->has_user = (access("/proc/self/ns/user", F_OK) == 0);
}

md_error_t namespaces_apply_prefork(const runtime_config_t *cfg) {
    /* If any parent-level configuration is needed before forking, do here */
    (void)cfg;
    return MD_SUCCESS;
}

md_error_t namespaces_apply_postfork_child(const runtime_config_t *cfg) {
    if (!cfg) return MD_ERR_INVALID_ARGS;

    int clone_flags = 0;

    if (cfg->ns_flags & MD_NS_UTS) {
        clone_flags |= CLONE_NEWUTS;
    }
    if (cfg->ns_flags & MD_NS_MOUNT) {
        clone_flags |= CLONE_NEWNS;
    }
    if (cfg->ns_flags & MD_NS_IPC) {
        clone_flags |= CLONE_NEWIPC;
    }
    if (cfg->ns_flags & MD_NS_NET) {
        clone_flags |= CLONE_NEWNET;
    }
    if (cfg->ns_flags & MD_NS_PID) {
        clone_flags |= CLONE_NEWPID;
    }

    if (clone_flags != 0) {
        log_debug("Calling unshare with flags: 0x%x", clone_flags);
        if (unshare(clone_flags) != 0) {
            int err = errno;
            if (err == EPERM) {
                log_error("Namespace creation denied (EPERM). Privilege (root/sudo) or user namespace capability required.");
            } else {
                md_perror("unshare", err);
            }
            return MD_ERR_NAMESPACE;
        }
    }

    /* Set hostname in UTS namespace if requested */
    if (cfg->hostname != NULL) {
        log_debug("Setting container hostname to '%s'", cfg->hostname);
        if (sethostname(cfg->hostname, strlen(cfg->hostname)) != 0) {
            md_perror("sethostname", errno);
            return MD_ERR_NAMESPACE;
        }
    }

    return MD_SUCCESS;
}
