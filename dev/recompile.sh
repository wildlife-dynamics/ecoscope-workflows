#!/bin/bash

example=$1
flags=$2

echo "recompiling example: ${example}"

command="pixi run --manifest-path src/ecoscope-workflows-ext-ecoscope/pyproject.toml --locked -e default \
ecoscope-workflows compile --spec examples/${example}/spec.yaml --clobber ${flags}"

exec $command
