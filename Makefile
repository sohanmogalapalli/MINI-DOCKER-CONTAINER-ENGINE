CC ?= gcc
CFLAGS ?= -std=c11 -Wall -Wextra -Wpedantic -Wshadow -Wconversion -Wformat=2 -D_GNU_SOURCE -Iinclude -O2 -MMD -MP
LDFLAGS ?=

SRC_DIR = src
INC_DIR = include
BUILD_DIR = build
BIN_DIR = bin
TEST_UNIT_DIR = tests/unit

SRCS = $(SRC_DIR)/cli.c \
       $(SRC_DIR)/config.c \
       $(SRC_DIR)/error.c \
       $(SRC_DIR)/log.c \
       $(SRC_DIR)/runtime.c \
       $(SRC_DIR)/process.c \
       $(SRC_DIR)/namespaces.c \
       $(SRC_DIR)/filesystem.c \
       $(SRC_DIR)/cgroups.c

OBJS = $(SRCS:$(SRC_DIR)/%.c=$(BUILD_DIR)/%.o)
MAIN_OBJ = $(BUILD_DIR)/main.o
DEPS = $(OBJS:.o=.d) $(MAIN_OBJ:.o=.d)

TARGET = $(BIN_DIR)/mini-docker
TEST_CONFIG_TARGET = $(BIN_DIR)/test_config
TEST_CGROUPS_TARGET = $(BIN_DIR)/test_cgroups_config

.PHONY: all clean test test-unit test-integration check dirs

all: dirs $(TARGET) $(TEST_CONFIG_TARGET) $(TEST_CGROUPS_TARGET)

dirs:
	@mkdir -p $(BUILD_DIR) $(BIN_DIR)

$(TARGET): $(OBJS) $(MAIN_OBJ)
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD_DIR)/test_config.o: $(TEST_UNIT_DIR)/test_config.c
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD_DIR)/test_cgroups_config.o: $(TEST_UNIT_DIR)/test_cgroups_config.c
	$(CC) $(CFLAGS) -c $< -o $@

$(TEST_CONFIG_TARGET): $(BUILD_DIR)/test_config.o $(BUILD_DIR)/config.o $(BUILD_DIR)/error.o $(BUILD_DIR)/log.o
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

$(TEST_CGROUPS_TARGET): $(BUILD_DIR)/test_cgroups_config.o $(BUILD_DIR)/cgroups.o $(BUILD_DIR)/config.o $(BUILD_DIR)/error.o $(BUILD_DIR)/log.o
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

test-unit: all
	@echo "--- Running Unit Tests ---"
	@$(TEST_CONFIG_TARGET)
	@$(TEST_CGROUPS_TARGET)

test-integration: all
	@echo "--- Running Integration Tests ---"
	@chmod +x tests/integration/*.sh scripts/*.sh
	@bash scripts/run_tests.sh

test: test-unit test-integration

check: $(TARGET)
	@$(TARGET) check

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR) tests/fixtures/rootfs

-include $(DEPS)
