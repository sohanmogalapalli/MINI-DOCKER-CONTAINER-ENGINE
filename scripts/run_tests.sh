#!/usr/bin/env bash
set -uo pipefail

echo "=========================================================="
echo "          Mini Docker Container Engine Test Suite         "
echo "=========================================================="

FAILED=0

echo -e "\n--- [1/2] Running Unit Tests ---"
if [ -f "./bin/test_config" ]; then
    ./bin/test_config || FAILED=$((FAILED + 1))
else
    echo "Unit test binary ./bin/test_config missing"
    FAILED=$((FAILED + 1))
fi

if [ -f "./bin/test_cgroups_config" ]; then
    ./bin/test_cgroups_config || FAILED=$((FAILED + 1))
else
    echo "Unit test binary ./bin/test_cgroups_config missing"
    FAILED=$((FAILED + 1))
fi

echo -e "\n--- [2/2] Running Integration Tests ---"
for t in tests/integration/*.sh; do
    if [ -f "$t" ]; then
        bash "$t" || FAILED=$((FAILED + 1))
    fi
done

echo -e "\n=========================================================="
if [ $FAILED -eq 0 ]; then
    echo " ALL TESTS COMPLETED SUCCESSFULLY!"
    echo "=========================================================="
    exit 0
else
    echo " $FAILED TEST(S) FAILED."
    echo "=========================================================="
    exit 1
fi
