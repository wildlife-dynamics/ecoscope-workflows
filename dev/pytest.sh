#!/bin/bash

namespace=$1
python_version=$2

command="pixi run \
--manifest-path src/ecoscope-workflows-${namespace}/pyproject.toml \
--locked --environment test-py${python_version} \
pytest src/ecoscope-workflows-${namespace}/tests -vx"

if [ -n "$3" ]; then
    marker=$3
    command="$command -m '$marker'"
fi

echo "Running command: $command"
eval $command
