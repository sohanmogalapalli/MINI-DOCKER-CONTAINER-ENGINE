#include "cli.h"
#include "log.h"
#include <getopt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MINI_DOCKER_VERSION "1.0.0"

void cli_print_version(void) {
    printf("mini-docker version %s (OS Course Educational Project)\n", MINI_DOCKER_VERSION);
    printf("Built for Linux container process isolation and cgroup v2 resource control.\n");
}

void cli_print_usage(const char *progname) {
    printf("Usage:\n");
    printf("  %s [GLOBAL OPTIONS] check\n", progname);
    printf("  %s [GLOBAL OPTIONS] run [OPTIONS] -- COMMAND [ARG...]\n", progname);
    printf("  %s --help\n", progname);
    printf("  %s --version\n\n", progname);
    printf("Commands:\n");
    printf("  check                  Inspect host environment, kernel namespaces, and cgroups\n");
    printf("  run                    Execute a command in an isolated container environment\n\n");
    printf("Run Options:\n");
    printf("  --hostname NAME        Set container hostname (automatically enables UTS namespace)\n");
    printf("  --uts                  Enable UTS (hostname) namespace isolation\n");
    printf("  --pid                  Enable PID namespace isolation (child sees itself as PID 1)\n");
    printf("  --mount                Enable Mount namespace isolation\n");
    printf("  --ipc                  Enable IPC (POSIX/SysV message queues, semaphores) namespace\n");
    printf("  --network              Enable Network namespace isolation (private loopback)\n");
    printf("  --rootfs PATH          Set container root filesystem directory\n");
    printf("  --memory LIMIT         Set cgroup v2 memory limit (e.g., 64M, 512K, 1G)\n");
    printf("  --cpu-quota VALUE      Set cgroup v2 CPU quota (e.g., 50000 or 50000/100000)\n");
    printf("  --cgroup-parent PATH   Parent cgroup v2 directory (default: /sys/fs/cgroup/mini-docker)\n\n");
    printf("Global Options:\n");
    printf("  -v, --verbose          Enable verbose debug diagnostics\n");
    printf("  -h, --help             Show this help message\n");
    printf("      --version          Show version information\n\n");
    printf("Examples:\n");
    printf("  %s check\n", progname);
    printf("  %s run -- /bin/echo \"Hello from child process\"\n", progname);
    printf("  %s run --uts --hostname container1 -- /bin/hostname\n", progname);
    printf("  %s run --pid --mount -- /bin/ps\n", progname);
    printf("  %s run --memory 64M -- /bin/sleep 2\n", progname);
}

static struct option long_options[] = {
    {"help",          no_argument,       0, 'h'},
    {"version",       no_argument,       0, 'V'},
    {"verbose",       no_argument,       0, 'v'},
    {"uts",           no_argument,       0, 'u'},
    {"hostname",      required_argument, 0, 'H'},
    {"pid",           no_argument,       0, 'p'},
    {"mount",         no_argument,       0, 'm'},
    {"ipc",           no_argument,       0, 'i'},
    {"network",       no_argument,       0, 'n'},
    {"rootfs",        required_argument, 0, 'r'},
    {"memory",        required_argument, 0, 'M'},
    {"cpu-quota",     required_argument, 0, 'C'},
    {"cgroup-parent", required_argument, 0, 'P'},
    {0, 0, 0, 0}
};

md_error_t cli_parse(int argc, char **argv, runtime_config_t *cfg) {
    if (argc < 2) {
        cli_print_usage(argv[0]);
        return MD_ERR_INVALID_ARGS;
    }

    /* Fast check for top-level help or version */
    if (strcmp(argv[1], "--help") == 0 || strcmp(argv[1], "-h") == 0) {
        cli_print_usage(argv[0]);
        exit(0);
    }
    if (strcmp(argv[1], "--version") == 0 || strcmp(argv[1], "-V") == 0) {
        cli_print_version();
        exit(0);
    }
    if (strcmp(argv[1], "check") == 0) {
        cfg->check_only = true;
        if (argc > 2 && (strcmp(argv[2], "-v") == 0 || strcmp(argv[2], "--verbose") == 0)) {
            cfg->verbose = true;
            log_init(true);
        }
        return MD_SUCCESS;
    }

    int opt_start = 1;
    if (strcmp(argv[1], "run") == 0) {
        opt_start = 2;
    }

    /* Reset getopt */
    optind = opt_start;
    int opt;
    while ((opt = getopt_long(argc, argv, "+hvupminH:r:M:C:P:V", long_options, NULL)) != -1) {
        switch (opt) {
            case 'h':
                cli_print_usage(argv[0]);
                exit(0);
            case 'V':
                cli_print_version();
                exit(0);
            case 'v':
                cfg->verbose = true;
                log_init(true);
                break;
            case 'u':
                cfg->ns_flags |= MD_NS_UTS;
                break;
            case 'H':
                cfg->ns_flags |= MD_NS_UTS; /* Setting hostname implies UTS namespace */
                if (cfg->hostname) free(cfg->hostname);
                cfg->hostname = strdup(optarg);
                break;
            case 'p':
                cfg->ns_flags |= MD_NS_PID;
                break;
            case 'm':
                cfg->ns_flags |= MD_NS_MOUNT;
                break;
            case 'i':
                cfg->ns_flags |= MD_NS_IPC;
                break;
            case 'n':
                cfg->ns_flags |= MD_NS_NET;
                break;
            case 'r':
                if (cfg->rootfs_path) free(cfg->rootfs_path);
                cfg->rootfs_path = strdup(optarg);
                cfg->ns_flags |= MD_NS_MOUNT; /* rootfs requires mount namespace */
                break;
            case 'M': {
                md_error_t err = config_parse_memory(optarg, &cfg->memory_limit_bytes);
                if (err != MD_SUCCESS) {
                    log_error("Invalid memory limit format: '%s' (use e.g. 64M, 1G)", optarg);
                    return err;
                }
                break;
            }
            case 'C': {
                md_error_t err = config_parse_cpu(optarg, &cfg->cpu_quota_us, &cfg->cpu_period_us);
                if (err != MD_SUCCESS) {
                    log_error("Invalid CPU quota format: '%s' (use e.g. 50000 or 50000/100000)", optarg);
                    return err;
                }
                break;
            }
            case 'P':
                if (cfg->cgroup_parent) free(cfg->cgroup_parent);
                cfg->cgroup_parent = strdup(optarg);
                break;
            case '?':
            default:
                cli_print_usage(argv[0]);
                return MD_ERR_INVALID_ARGS;
        }
    }

    /* Anything after options or '--' is the target command */
    if (optind < argc) {
        /* If the next token was '--', optind now points to the command right after it */
        cfg->command_argv = &argv[optind];
        cfg->command_argc = argc - optind;
    } else {
        log_error("Missing target command. Syntax: %s run [OPTIONS] -- COMMAND [ARGS...]", argv[0]);
        return MD_ERR_INVALID_ARGS;
    }

    return config_validate(cfg);
}
