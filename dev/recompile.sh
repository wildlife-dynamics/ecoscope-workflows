#!/bin/bash

example=$1

pixi run --manifest-path src/ecoscope-workflows-ext-ecoscope/pyproject.toml --locked -e default \
ecoscope-workflows compile --spec examples/${example}/spec.yaml --clobber --lock
