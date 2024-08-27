#!/bin/bash

TEMPLATES=(
    "jupytext"
    "script-sequential"
    "script-async"
)

# Generate dag and json/yaml params for each spec in "examples/compilation-specs/"
for spec in examples/compilation-specs/*.yaml; do
    specname=$(basename "${spec}" ".yaml")
    for template in "${TEMPLATES[@]}"; do
        ecoscope-workflows compile --spec "${spec}" --template "${template}.jinja2" --outpath "examples/dags/${specname//-/_}_dag.${template//-/_}.py"
        done
    ecoscope-workflows get-params --spec "${spec}" --format json --outpath "examples/params/${specname//-/_}_params_fillable.json"
    ecoscope-workflows get-params --spec "${spec}" --format yaml --outpath "examples/params/${specname//-/_}_params_fillable.yaml"
    done
