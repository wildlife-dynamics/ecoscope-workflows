#!/bin/bash

set -e

example=$1
execution_mode=$2
mock_io=true
port=4000
results_url=/workflow/results  # must be consistent with volume mount set in docker-run.sh
params=$(yq -c '.test1.params' examples/${example}/test-cases.yaml)

curl -X POST "http://localhost:${port}/?execution_mode=${execution_mode}&mock_io=${mock_io}&results_url=${results_url}" \
-H "Content-Type: application/json" \
-d '{"params": '"${params}"'}'
