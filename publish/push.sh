#!/bin/bash

for file in vendor/artifacts/**/*.conda; do
    rattler-build upload prefix -c ecoscope-workflows "$file" || true
done
