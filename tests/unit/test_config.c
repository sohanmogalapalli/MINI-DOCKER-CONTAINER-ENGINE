#include "config.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int g_tests_run = 0;
static int g_tests_passed = 0;

#define TEST_ASSERT(cond, msg) do { \
    g_tests_run++; \
    if (cond) { \
        g_tests_passed++; \
    } else { \
        printf("FAILED: %s (line %d)\n", msg, __LINE__); \
    } \
} while (0)

static void test_memory_parsing(void) {
    uint64_t bytes = 0;

    /* Valid forms */
    TEST_ASSERT(config_parse_memory("128M", &bytes) == MD_SUCCESS && bytes == 128ULL * 1024 * 1024, "128M parsed correctly");
    TEST_ASSERT(config_parse_memory("64MB", &bytes) == MD_SUCCESS && bytes == 64ULL * 1024 * 1024, "64MB parsed correctly");
    TEST_ASSERT(config_parse_memory("1G", &bytes) == MD_SUCCESS && bytes == 1ULL * 1024 * 1024 * 1024, "1G parsed correctly");
    TEST_ASSERT(config_parse_memory("512K", &bytes) == MD_SUCCESS && bytes == 512ULL * 1024, "512K parsed correctly");
    TEST_ASSERT(config_parse_memory("1024", &bytes) == MD_SUCCESS && bytes == 1024ULL, "Plain integer parsed correctly");

    /* Invalid forms */
    TEST_ASSERT(config_parse_memory("", &bytes) != MD_SUCCESS, "Empty string rejected");
    TEST_ASSERT(config_parse_memory("-128M", &bytes) != MD_SUCCESS, "Negative value rejected");
    TEST_ASSERT(config_parse_memory("abc", &bytes) != MD_SUCCESS, "Alpha string rejected");
    TEST_ASSERT(config_parse_memory("128Z", &bytes) != MD_SUCCESS, "Invalid unit rejected");
    TEST_ASSERT(config_parse_memory("99999999999999999999999999999G", &bytes) != MD_SUCCESS, "Overflow rejected");
}

static void test_cpu_parsing(void) {
    uint64_t quota = 0, period = 0;

    TEST_ASSERT(config_parse_cpu("50000", &quota, &period) == MD_SUCCESS && quota == 50000 && period == 100000, "50000 quota parsed");
    TEST_ASSERT(config_parse_cpu("20000/50000", &quota, &period) == MD_SUCCESS && quota == 20000 && period == 50000, "20000/50000 parsed");
    TEST_ASSERT(config_parse_cpu("0", &quota, &period) != MD_SUCCESS, "Zero quota rejected");
    TEST_ASSERT(config_parse_cpu("-5000", &quota, &period) != MD_SUCCESS, "Negative quota rejected");
}

static void test_hostname_validation(void) {
    runtime_config_t cfg;
    config_init(&cfg);

    char *cmd[] = {"/bin/echo", "test", NULL};
    cfg.command_argv = cmd;
    cfg.command_argc = 2;

    /* Valid hostnames */
    cfg.hostname = strdup("my-container-1");
    TEST_ASSERT(config_validate(&cfg) == MD_SUCCESS, "Valid hostname accepted");
    free(cfg.hostname);

    /* Invalid hostnames */
    cfg.hostname = strdup("invalid_hostname_with_underscore_or_spaces 123");
    TEST_ASSERT(config_validate(&cfg) != MD_SUCCESS, "Invalid character rejected");
    free(cfg.hostname);

    /* Missing command */
    cfg.hostname = NULL;
    cfg.command_argc = 0;
    cfg.command_argv = NULL;
    TEST_ASSERT(config_validate(&cfg) != MD_SUCCESS, "Missing command rejected");

    config_free(&cfg);
}

int main(void) {
    printf("Running unit tests for configuration parser...\n");
    test_memory_parsing();
    test_cpu_parsing();
    test_hostname_validation();

    printf("Tests completed: %d / %d passed.\n", g_tests_passed, g_tests_run);
    return (g_tests_passed == g_tests_run) ? 0 : 1;
}
