#include "log.h"
#include <stdarg.h>
#include <stdio.h>

static bool g_verbose = false;

void log_init(bool verbose) {
    g_verbose = verbose;
}

void log_info(const char *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    fprintf(stderr, "[mini-docker] INFO: ");
    vfprintf(stderr, fmt, args);
    fprintf(stderr, "\n");
    va_end(args);
}

void log_debug(const char *fmt, ...) {
    if (!g_verbose) {
        return;
    }
    va_list args;
    va_start(args, fmt);
    fprintf(stderr, "[mini-docker] DEBUG: ");
    vfprintf(stderr, fmt, args);
    fprintf(stderr, "\n");
    va_end(args);
}

void log_warn(const char *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    fprintf(stderr, "[mini-docker] WARN: ");
    vfprintf(stderr, fmt, args);
    fprintf(stderr, "\n");
    va_end(args);
}

void log_error(const char *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    fprintf(stderr, "[mini-docker] ERROR: ");
    vfprintf(stderr, fmt, args);
    fprintf(stderr, "\n");
    va_end(args);
}
