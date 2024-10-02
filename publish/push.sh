#!/bin/bash

for file in /tmp/ecoscope-workflows/release/artifacts/**/*.conda; do
    rattler-build upload prefix -c ecoscope-workflows "$file" || true
done
