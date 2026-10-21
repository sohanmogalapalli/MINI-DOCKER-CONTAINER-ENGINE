#include "cgroups.h"
#include <assert.h>
#include <stdio.h>
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

static void test_cgroups_probe(void) {
    cgroup_support_t support;
    cgroups_probe_support(&support);

    /* On modern Linux/WSL2, cgroup2 should be mounted */
    printf("  [probe] cgroup2 mounted: %s\n", support.cgroup2_mounted ? "YES" : "NO");
    printf("  [probe] memory controller: %s\n", support.has_memory ? "YES" : "NO");
    printf("  [probe] cpu controller: %s\n", support.has_cpu ? "YES" : "NO");

    TEST_ASSERT(strlen(support.root_path) > 0, "cgroup root path is non-empty");
}

static void test_cgroups_context(void) {
    runtime_config_t cfg;
    config_init(&cfg);
    cfg.memory_limit_bytes = 64ULL * 1024 * 1024;

    cgroup_ctx_t ctx;
    memset(&ctx, 0, sizeof(ctx));

    /* Test dry context with invalid config */
    TEST_ASSERT(cgroups_init_context(NULL, 1234, &ctx) != MD_SUCCESS, "NULL config rejected");

    config_free(&cfg);
}

int main(void) {
    printf("Running unit tests for cgroups...\n");
    test_cgroups_probe();
    test_cgroups_context();

    printf("Cgroups tests completed: %d / %d passed.\n", g_tests_passed, g_tests_run);
    return (g_tests_passed == g_tests_run) ? 0 : 1;
}
