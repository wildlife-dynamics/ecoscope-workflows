#!/bin/bash

example=$1

command="pixi run \
--manifest-path examples/${example}/ecoscope-workflows-${example}-workflow/pixi.toml \
--locked --environment default \
docker-build"

eval $command
