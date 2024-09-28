#!/bin/bash

example=$1
results_dir=.ecoscope-workflows-tmp/${example}-workflow-results

docker run -d -v $(pwd)/${results_dir}:/workflow/results -e PORT=4000 -p 4000:4000 ecoscope-workflows-${example}-workflow
