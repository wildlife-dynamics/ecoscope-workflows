# ecoscope-workflows

An extensible task specification and compiler for local and distributed workflows.

## Installation

To install with test dependencies, in a virtual environment with Python >= 3.10, run:

```console
$ pip install -e ".[test]"
```

## Key concepts

In `ecoscope-workflows`, _**tasks**_ (python functions) are composed into DAGs
via _**compilation specs**_ defined in YAML. These specs can then be compiled
to various targets including serial Python scripts and Airflow DAGs, via the
`ecoscope-workflows` CLI.

### Tasks

Tasks are strongly-typed Python functions wrapping a unit of work to be
completed as the node of a Directed Acyclic Graph (DAG). In pseudocode,
with comments describing the key features of a task definition:

```python
# python's builtin annotated type let's us attach extra metadata to
# function parameters, such as descriptions which can be used if the
# task is to be configured through a form-based web interface. it is
# also essential to leverage pydantic's validation machinery.
from typing import Annotated

# we leverage pydantic to augment that function metadata for ease of
# introspection and type parsing/coercion in the distributed context
from pydantic import Field

# we define some of our own custom subscriptable annotations as well.
# the `DataFrame` type allows us to require input and output data to
# our task conforms to expected schemas
from ecoscope_workflows.annotations import DataFrame
# finally, our `@distributed` decorator gives us the ability to auto-
# magically deserialize inputs and/or serialize outputs to the task,
# if the workflow compilation target requires it. also, it lets us
# attach top-level metadata to the task such as an `image`, container
# resource requirements, and `tags` for sorting and categorization.
from ecoscope_workflows.decorators import distributed

# if a task handles tabular data, than both the input and output
# data require a schema, which is subscripted to our `DataFrame`
# annotation. this allows us to check task compatibility at DAG
# compile time, prevent mis-matching of tasks, and validate data
# for correctness before releasing it to downstream tasks.
InputSchema = ...
OutputSchema = ...


@distributed(image="custom-image:latest", tags=["foo"])
def my_cool_analysis_task(
    input_dataframe: DataFrame[InputSchema],
    some_int_parameter: Annotated[
        int,
        Field(default=1, description="An integer used for math."),
    ],
    another_float_parameter: Annotated[
        float,
        Field(default=2.0, description="An float, for math."),
    ],
) -> DataFrame[OutputSchema]:
    # contrary to standard python convention, imports of any heavy
    # data analysis dependencies are deferred to the function scope.
    # this allows the compiler to import tasks and introspect their
    # call signatures, without requiring `awesome_pydata_package` to
    # exist in the compilation/parsing environment. for serialization
    # purposes as well, this type of import deferral is helpful and
    # therefore not uncommon when using python in distributed settings.
    from heavy_duty_pydata_package import cool_analysis

    return cool_analysis(
        input_dataframe,
        some_int_parameter,
        another_float_parameter,
    )
```
- **T

## CLI Quickstart

```console
$ ecoscope-workflows --help
usage: ecoscope-workflows [-h] {compile,tasks,get-params} ...

options:
  -h, --help            show this help message and exit

subcommands:
  {compile,tasks,get-params}
    compile             Compile workflows
    tasks               Manage tasks
    get-params          Get params
```


## Development

### Tasks

```python

```

### Workflows
