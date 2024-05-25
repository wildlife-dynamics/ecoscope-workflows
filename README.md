# ecoscope-workflows

An extensible task specification and compiler for local and distributed workflows.

## Installation

To install with test dependencies, in a virtual environment with Python >= 3.10, run:

```console
$ pip install -e ".[test]"
```

## Key concepts

In `ecoscope-workflows`, [_**tasks**_](#tasks) (python functions) are composed into DAGs
via [_**compilation specs**_](#compilation-specs) defined in YAML. These specs can then be compiled
to various targets including serial Python scripts (to run locally) and Airflow DAGs (to run on Kubernetes),
via the [`ecoscope-workflows` _**CLI**_](#compilation-specs). Finally, the
[_**extensible task registry**_](#extensible-task-registry) supports registration of user-defined
and third-party tasks.

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
    # exist in the compilation/parsing environment. this becomes
    # especially valuable when you consider that each task is capable
    # of being run in a totally isolated container environment, so
    # these "inner" task dependencies (versions, etc.) do not necessarily
    # need to be compatible with those of other tasks in the same DAG.
    from heavy_duty_pydata_package import cool_analysis

    return cool_analysis(
        input_dataframe,
        some_int_parameter,
        another_float_parameter,
    )
```

### Compilation specs

### CLI Quickstart

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

### Extensible task registry

Don't see the task you want here already? First, check the
[`task-request` label on the issue tracker](https://github.com/wildlife-dynamics/ecoscope-workflows/labels/task-request)
to see if anyone else has requested this task. If not, please raise an issue describing your requested task!
This will give you an opportunity to crowdsource implementation ideas from the core team and community.

It's possible your request will become a built-in task in `ecoscope-workflows` one day! But until then,
we provide an means for extending the tasks visible to the compilation environment via Python's entry points.

To extend the task registry, simply:

1. Create an installable Python package that incudes a module named `tasks`
2. In `tasks`, define your extension tasks using the `@distibuted` decorator, and adhering to the other
style conventions described in [tasks](#tasks) above.
3. In your package's `pyproject.toml`, use `projects.entry-points` to associate the fully qualified
(i.e., absolute) import path for your tasks module with the `"ecoscope_workflows".tasks` entry point. For example:

```toml
# pyproject.toml

[project]
dependencies = ["ecoscope_workflows"]

[project.entry-points."ecoscope_workflows"]
# here we are imagining that your extension package is importable as `my_extension_package`,
# but you will no doubt think of a catchier name than that! note that you must provide a
# top-level `.tasks` module, i.e.:
tasks = "my_extension_package.tasks"
```

With these steps in place, simply install your package in the compilation Python environment, and then run:
```console
$ ecoscope-workflows tasks
```
You should see your extension packages listed and can now freely use them in [compilation specs](#compilation-specs).

> This same mechanism is how the built-in tasks are collected as well! If you're curious how this works,
> check out the `pyproject.toml` for our package, as well as the `registry` module. This design is
> [inspired by `fsspec`](https://filesystem-spec.readthedocs.io/en/latest/developer.html#implementing-a-backend).
