#ifndef MINI_DOCKER_PROCESS_H
#define MINI_DOCKER_PROCESS_H

#include "config.h"
#include "error.h"
#include <sys/types.h>

typedef struct {
    int sync_pipe_c2p[2]; /* Child to Parent: Child tells parent its PID or ready */
    int sync_pipe_p2c[2]; /* Parent to Child: Parent tells child setup (cgroup) is ready to exec */
} process_sync_t;

md_error_t process_sync_init(process_sync_t *sync);
void process_sync_init_in_parent(process_sync_t *sync);
void process_sync_init_in_child(process_sync_t *sync);
void process_sync_destroy(process_sync_t *sync);
md_error_t process_sync_wait_for_parent(process_sync_t *sync);
md_error_t process_sync_notify_child(process_sync_t *sync);
md_error_t process_exec(const runtime_config_t *cfg);
int process_wait(pid_t pid);

#endif /* MINI_DOCKER_PROCESS_H */
