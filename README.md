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

Compilation specs define a DAG of known [tasks](#tasks), which can either be built-ins,
or tasks registered via the [extensible task registry](#extensible-task-registry).

The inline comments in this example explain what each line means:

```yaml
# the workflow name
name: calculate_time_density
# for distibuted compilation targets (e.g. Airflow), this is where task
# results will be serialized for passing between nodes (i.e. tasks)
cache_root: gcs://my-bucket/ecoscope/cache/dag-runs
# the tasks. these names either have to be built-ins or third-party registrations
# via the "ecoscope_workflows.tasks" entry point. to see a list of known tasks for
# a given python environment, from the terminal, run `ecoscope-workflows tasks` to
# dump the current task registry to stdout.
tasks:
  # root tasks (which have no dependencies on the output of other tasks) are specified
  # by their name, followed by empty curly braces, like so:
  get_subjectgroup_observations: {}
  # this next task has a dependency defined within it...
  process_relocations:
    # this means, that the `process_relocations` task takes an argument `observations`,
    # and we want the value passed to this argument to be the return value of the task
    # `get_subjectgroup_observations`, which is the root task of this workflow.
    observations: get_subjectgroup_observations
  relocations_to_trajectory:
    # the pattern continues: `relocations_to_trajectory` has an argument named
    # `relocations`. populate its value from the return value of `process_relocations`
    relocations: process_relocations
  calculate_time_density:
    # etc.
    trajectory_gdf: relocations_to_trajectory
  draw_ecomap:
    # and etc., until the last task!
    geodataframe: calculate_time_density
```

Note that any arguments for a [task](#task) not specified in the spec will need to be passed
at the time the workflow (script, Airflow DAG, etc.) is invoked. The following command

```console
$ ecoscope-workflows get-params --spec ${PATH_TO_SPEC}
```
will return these invocation-time parameters as either jsonschema (for programmatic consumption)
or as a fillable yaml form (for humans); use the `--format` option to choose!

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


## Example workflows development

To develop an new example workflow:

1. Implement and test any necessary additional built-in [tasks](#tasks), adding them to the `.tasks`
submodule that best fits their use:
- `io`: Fetching data from third parties. Anthing requiring a client, token, credentials, etc. should go here.
- `preprocessing`: Munging data prior to analysis
- `analysis`: Performing an analytical function.
- `results`: Encapulating the output of analyses as maps, summary tables, etc.
2. Define a YAML [compilation spec](#compilation-specs) and put it in `examples/compilation-specs`
3. Manually compile the spec to an example script for public reference, e.g.
```console
$ ecoscope-workflows compile \
--spec examples/compilation-specs/${WORKFLOW_NAME}.yaml \
--template script-sequential.jinja2 \
--outpath examples/dags/${WORKFLOW_NAME}_dag.script_sequential.py
```
4. Export its parameters in both jsonschema, and fillable yaml formats, for reference, as well:

As jsonschema:

```console
$ ecoscope-workflows get-params \
--spec examples/compilation-specs/${WORKFLOW_NAME}.yaml \
--format json \
--outpath examples/dags/${WORKFLOW_NAME}_params.yaml
```

As  fillable yaml:

```console
$ ecoscope-workflows get-params \
--spec examples/compilation-specs/${WORKFLOW_NAME}.yaml \
--format yaml \
--outpath examples/dags/${WORKFLOW_NAME}_params.yaml
```

### Running the script

1. Copy the fillable yaml file you generated above into a scratch directory outside
this repo
2. Fill in the yaml form with representative values for each parameter
3. From the repo root, run the script with:
```console
$ python3 examples/dags/${WORKFLOW_NAME}_dag.script_sequential.py \
--config ${PATH_TO_FILLED_YAML_PARAM_FILE}
```

### Testing and debugging

```
TODO: `ecoscope-workflows compile` offers a useful `--testing` mode which allows for
mocking the output of tasks in a compiled DAG using example data packaged alongside
the task definition. Documentation for this feature is forthcoming!
```
