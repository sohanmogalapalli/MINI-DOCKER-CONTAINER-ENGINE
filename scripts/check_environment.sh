#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "   Mini Docker Container Engine - Environment Diagnostic   "
echo "=========================================================="

if [ -f "./bin/mini-docker" ]; then
    ./bin/mini-docker check
else
    echo "mini-docker executable not built yet. Run 'make' first."
fi
