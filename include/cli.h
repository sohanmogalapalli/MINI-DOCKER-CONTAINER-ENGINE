#ifndef MINI_DOCKER_CLI_H
#define MINI_DOCKER_CLI_H

#include "config.h"

void cli_print_usage(const char *progname);
void cli_print_version(void);
md_error_t cli_parse(int argc, char **argv, runtime_config_t *cfg);

#endif /* MINI_DOCKER_CLI_H */
