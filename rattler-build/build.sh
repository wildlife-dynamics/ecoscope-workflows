#!/bin/bash

DEPENDENCIES=(
    "ps-mem"
    "lithops"
    # "earthranger-client"
    # "lonboard"
    # "ecoscope-core"
)

for dep in "${DEPENDENCIES[@]}"; do
    echo "Building $dep"
    rattler-build build --recipe $(pwd)/rattler-build/recipes/${dep}.yaml --output-dir $(pwd)/rattler-build/artifacts --skip-existing=all
    done
