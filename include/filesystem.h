#ifndef MINI_DOCKER_FILESYSTEM_H
#define MINI_DOCKER_FILESYSTEM_H

#include "config.h"
#include "error.h"

md_error_t fs_validate_rootfs(const char *rootfs_path);
md_error_t fs_setup_rootfs(const runtime_config_t *cfg);

#endif /* MINI_DOCKER_FILESYSTEM_H */
