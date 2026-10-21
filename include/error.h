#ifndef MINI_DOCKER_ERROR_H
#define MINI_DOCKER_ERROR_H

typedef enum {
    MD_SUCCESS = 0,
    MD_ERR_INVALID_ARGS = 1,
    MD_ERR_CONFIG = 2,
    MD_ERR_SYSCALL = 3,
    MD_ERR_NAMESPACE = 4,
    MD_ERR_FILESYSTEM = 5,
    MD_ERR_CGROUPS = 6,
    MD_ERR_EXEC = 7,
    MD_ERR_CHILD_FAILED = 8,
    MD_ERR_NOT_SUPPORTED = 9
} md_error_t;

const char *md_error_string(md_error_t code);
void md_perror(const char *op, int errnum);

#endif /* MINI_DOCKER_ERROR_H */
