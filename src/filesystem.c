#include "filesystem.h"
#include "log.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <unistd.h>

md_error_t fs_validate_rootfs(const char *rootfs_path) {
    if (!rootfs_path || *rootfs_path == '\0') {
        log_error("Invalid rootfs path provided");
        return MD_ERR_FILESYSTEM;
    }

    struct stat st;
    if (stat(rootfs_path, &st) != 0) {
        md_perror("stat rootfs path", errno);
        return MD_ERR_FILESYSTEM;
    }

    if (!S_ISDIR(st.st_mode)) {
        log_error("Rootfs path '%s' is not a directory", rootfs_path);
        return MD_ERR_FILESYSTEM;
    }

    /* Check access permissions (read and execute) */
    if (access(rootfs_path, R_OK | X_OK) != 0) {
        md_perror("access rootfs path", errno);
        return MD_ERR_FILESYSTEM;
    }

    return MD_SUCCESS;
}

md_error_t fs_setup_rootfs(const runtime_config_t *cfg) {
    if (!cfg || !cfg->rootfs_path) {
        return MD_SUCCESS; /* No rootfs requested */
    }

    const char *target = cfg->rootfs_path;
    log_debug("Setting up filesystem isolation with rootfs: %s", target);

    /* 1. Make all mounts in our mount namespace private to avoid host propagation */
    if (mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) != 0) {
        md_perror("mount MS_PRIVATE", errno);
        log_warn("Failed to set mount propagation to MS_PRIVATE (may require root privileges)");
    }

    /* 2. Bind mount rootfs to itself to ensure it is an independent mountpoint */
    if (mount(target, target, "bind", MS_BIND | MS_REC, NULL) != 0) {
        md_perror("mount bind rootfs", errno);
        return MD_ERR_FILESYSTEM;
    }

    /* 3. Check if /proc exists in the target rootfs, mount proc if present */
    char proc_path[1024];
    snprintf(proc_path, sizeof(proc_path), "%s/proc", target);
    struct stat st;
    if (stat(proc_path, &st) == 0 && S_ISDIR(st.st_mode)) {
        log_debug("Mounting /proc in container rootfs at %s", proc_path);
        if (mount("proc", proc_path, "proc", 0, NULL) != 0) {
            md_perror("mount proc", errno);
            log_warn("Failed to mount /proc in rootfs");
        }
    }

    /* 4. Perform chroot */
    log_debug("Entering chroot: %s", target);
    if (chroot(target) != 0) {
        md_perror("chroot", errno);
        return MD_ERR_FILESYSTEM;
    }

    /* 5. Change current directory to container root */
    if (chdir("/") != 0) {
        md_perror("chdir /", errno);
        return MD_ERR_FILESYSTEM;
    }

    log_debug("Filesystem isolation active at /");
    return MD_SUCCESS;
}
