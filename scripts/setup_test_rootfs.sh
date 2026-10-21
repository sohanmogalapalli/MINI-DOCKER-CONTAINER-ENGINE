#!/usr/bin/env bash
set -euo pipefail

ROOTFS_DIR="./tests/fixtures/rootfs"
mkdir -p "$ROOTFS_DIR/bin" "$ROOTFS_DIR/proc" "$ROOTFS_DIR/dev" "$ROOTFS_DIR/etc"

# Compile a tiny static helper executable inside rootfs
cat << 'EOF' > "$ROOTFS_DIR/init.c"
#include <stdio.h>
#include <unistd.h>

int main(void) {
    printf("HELLO_FROM_ROOTFS\n");
    return 0;
}
EOF

gcc -static "$ROOTFS_DIR/init.c" -o "$ROOTFS_DIR/bin/init"
rm -f "$ROOTFS_DIR/init.c"

echo "Minimal rootfs initialized at $ROOTFS_DIR"
