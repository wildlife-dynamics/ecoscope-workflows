#!/bin/bash

example=$1
api=$2
mode=$3

command="pixi run \
--manifest-path examples/${example}/ecoscope-workflows-${example}-workflow/pixi.toml \
--locked --environment test \
test-${api}-${mode}-mock-io --case test1"

eval $command
