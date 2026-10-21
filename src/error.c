#include "error.h"
#include <stdio.h>
#include <string.h>

const char *md_error_string(md_error_t code) {
    switch (code) {
        case MD_SUCCESS:
            return "Success";
        case MD_ERR_INVALID_ARGS:
            return "Invalid arguments";
        case MD_ERR_CONFIG:
            return "Configuration validation failed";
        case MD_ERR_SYSCALL:
            return "System call error";
        case MD_ERR_NAMESPACE:
            return "Namespace setup error";
        case MD_ERR_FILESYSTEM:
            return "Filesystem or rootfs error";
        case MD_ERR_CGROUPS:
            return "cgroup v2 resource controller error";
        case MD_ERR_EXEC:
            return "Command execution failed";
        case MD_ERR_CHILD_FAILED:
            return "Child process exited with failure";
        case MD_ERR_NOT_SUPPORTED:
            return "Feature not supported by kernel/environment";
        default:
            return "Unknown error";
    }
}

void md_perror(const char *op, int errnum) {
    if (op != NULL && errnum != 0) {
        fprintf(stderr, "[mini-docker] ERROR: %s: %s (errno=%d)\n", op, strerror(errnum), errnum);
    } else if (op != NULL) {
        fprintf(stderr, "[mini-docker] ERROR: %s\n", op);
    }
}
