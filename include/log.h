#ifndef MINI_DOCKER_LOG_H
#define MINI_DOCKER_LOG_H

#include <stdio.h>
#include <stdbool.h>

void log_init(bool verbose);
void log_info(const char *fmt, ...);
void log_debug(const char *fmt, ...);
void log_warn(const char *fmt, ...);
void log_error(const char *fmt, ...);

#endif /* MINI_DOCKER_LOG_H */
