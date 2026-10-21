#ifndef MINI_DOCKER_RUNTIME_H
#define MINI_DOCKER_RUNTIME_H

#include "config.h"

int runtime_check_environment(void);
int runtime_run(const runtime_config_t *cfg);

#endif /* MINI_DOCKER_RUNTIME_H */
