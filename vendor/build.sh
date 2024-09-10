#!/bin/bash

DEPENDENCIES=(
    "ps-mem"
    "lithops"
    "earthranger-client"
    "lonboard"
    "ecoscope-core"
)

for dep in "${DEPENDENCIES[@]}"; do
    echo "Building $dep"
    rattler-build build \
    --recipe $(pwd)/vendor/recipes/${dep}.yaml \
    --output-dir $(pwd)/vendor/artifacts \
    --skip-existing=all
done
