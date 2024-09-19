#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <vendor|release>"
    exit 1
fi

if [ "$1" == "vendor" ]; then
    RECIPES=(
        "vendor/ps-mem"
        "vendor/lithops"
        "vendor/earthranger-client"
        "vendor/lonboard"
        "vendor/ecoscope-core"
    )
elif [ "$1" == "release" ]; then
    RECIPES=(
        "release/ecoscope-workflows-core"
        "release/ecoscope-workflows-ext-ecoscope"
    )
else
  echo "Invalid argument. Please use 'vendor' or 'release'."
  exit 1
fi

echo "You selected: $1"
echo "Building recipes: ${RECIPES[@]}"

for rec in "${RECIPES[@]}"; do
    echo "Building $rec"
    rattler-build build \
    --recipe $(pwd)/publish/recipes/${rec}.yaml \
    --output-dir /tmp/ecoscope-workflows/release/artifacts \
    --skip-existing=all
done
