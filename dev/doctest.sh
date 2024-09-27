#!/bin/bash

namespace=$1
python_version=$2

pixi run \
--manifest-path src/ecoscope-workflows-${namespace}/pyproject.toml \
--locked --environment test-py${python_version} \
pytest -v src/ecoscope-workflows-${namespace} \
--doctest-modules
