#!/bin/bash

set -e

export COMMIT_SHA=$1

echo "Building container for commit $COMMIT_SHA"

export ECOSCOPE_WORKFLOWS_REV=${COMMIT_SHA}
export TMP_RATTLER_RECIPE=`pwd`/tmp/${COMMIT_SHA}.yaml
export TMP_ENVFILE=./tmp/environment.yml

echo "Creating temporary rattler recipe file $TMP_RATTLER_RECIPE"
python scripts/set_context_version.py `pwd`/rattler/ecoscope-workflows.yaml $TMP_RATTLER_RECIPE $ECOSCOPE_WORKFLOWS_REV

echo "Calling rattler-build on $TMP_RATTLER_RECIPE"
rattler-build build --recipe $TMP_RATTLER_RECIPE

echo "Creating temporary environment file $TMP_ENVFILE"
python scripts/set_envyaml_workflows_specifier.py `pwd`/environment.yml $TMP_ENVFILE $ECOSCOPE_WORKFLOWS_REV

echo "Building container with $TMP_ENVFILE"
docker buildx build -t `echo $COMMIT_SHA | cut -c1-7` \
    --target=testable_runtime \  # This is the target we want to build for testing
    -f Dockerfile --build-arg ENVFILE=$TMP_ENVFILE .
