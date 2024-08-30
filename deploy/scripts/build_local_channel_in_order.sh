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
    rattler-build build --recipe rattler/${dep}.yaml --skip-existing=all
    done
