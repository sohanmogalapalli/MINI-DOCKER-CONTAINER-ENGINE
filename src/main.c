#include "cli.h"
#include "config.h"
#include "log.h"
#include "runtime.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    runtime_config_t config;
    config_init(&config);

    md_error_t parse_res = cli_parse(argc, argv, &config);
    if (parse_res != MD_SUCCESS) {
        config_free(&config);
        return (int)parse_res;
    }

    int ret = runtime_run(&config);

    config_free(&config);
    return ret;
}
