#!/bin/bash

DEPENDENCIES=(
    "ps-mem"
    "lithops"
    "earthranger-client"
    "lonboard"
    "ecoscope-core"
)

PLATFORMS=(
    "linux-aarch64"
    "linux-64"
    "osx-64"
)

for dep in "${DEPENDENCIES[@]}"; do
    for platform in "${PLATFORMS[@]}"; do
        echo "Building $dep for $platform"
        rattler-build build \
        --recipe $(pwd)/vendor/recipes/${dep}.yaml \
        --target-platform $platform \
        --output-dir $(pwd)/vendor/artifacts \
        --skip-existing=all
    done
done
