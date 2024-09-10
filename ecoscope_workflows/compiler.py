import builtins
import functools
import keyword
import pathlib
import subprocess
import sys
from typing import Annotated, Any, Callable, Literal, TypeAlias, TypeVar

from jinja2 import Environment, FileSystemLoader
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PlainSerializer,
    computed_field,
    field_validator,
    model_serializer,
    model_validator,
)
from pydantic.functional_validators import AfterValidator, BeforeValidator

from ecoscope_workflows.jsonschema import ReactJSONSchemaFormConfiguration
from ecoscope_workflows.registry import KnownTask, known_tasks

T = TypeVar("T")

TEMPLATES = pathlib.Path(__file__).parent / "templates"


class _ForbidExtra(BaseModel):
    model_config = ConfigDict(extra="forbid")


class _WorkflowVariable(BaseModel):
    """Base class for workflow variables."""

    value: str


class TaskIdVariable(_WorkflowVariable):
    """A variable that references the return value of another task in the workflow."""

    suffix: Literal["return"]

    @model_serializer
    def serialize(self) -> str:
        return self.value


class EnvVariable(_WorkflowVariable):
    """A variable that references an environment variable."""

    @model_serializer
    def serialize(self) -> str:
        return f'os.environ["{self.value}"]'


def _parse_variable(s: str) -> TaskIdVariable | EnvVariable:
    if not (s.startswith("${{") and s.endswith("}}")):
        raise ValueError(
            f"`{s}` is not a valid variable. " "Variables must be wrapped in `${{ }}`."
        )
    inner = s.replace("${{", "").replace("}}", "").strip()
    match inner.split("."):
        case ["workflow", task_id, suffix]:
            return TaskIdVariable(value=task_id, suffix=suffix)
        case ["env", env_var_name]:
            return EnvVariable(value=env_var_name)
        case _:
            raise ValueError(
                "Unrecognized variable format. Expected one of: "
                "`${{ workflow.<task_id>.<suffix> }}`, "
                "`${{ env.<ENV_VAR_NAME> }}`."
            )


def _parse_variables(
    s: str | list[str],
) -> TaskIdVariable | EnvVariable | list[TaskIdVariable | EnvVariable]:
    if isinstance(s, str):
        return _parse_variable(s)
    return [_parse_variable(v) for v in s]


def _is_identifier(s: str):
    if not s.isidentifier():
        raise ValueError(f"`{s}` is not a valid python identifier.")
    return s


def _is_not_reserved(s: str):
    assert _is_identifier(s)
    if keyword.iskeyword(s):
        raise ValueError(f"`{s}` is a python keyword.")
    if s in dir(builtins):
        raise ValueError(f"`{s}` is a built-in python function.")
    return s


def _is_valid_task_instance_id(s: str):
    if s in known_tasks:
        raise ValueError(f"`{s}` is a registered known task name.")
    if len(s) > 32:
        raise ValueError(f"`{s}` is too long; max length is 32 characters.")
    return s


def _is_known_task_name(s: str):
    if s not in known_tasks:
        raise ValueError(f"`{s}` is not a registered known task name.")
    return s


def _is_valid_spec_name(s: str):
    if len(s) > 64:
        raise ValueError(f"`{s}` is too long; max length is 64 characters.")
    return s


WorkflowVariable = Annotated[
    TaskIdVariable | EnvVariable, BeforeValidator(_parse_variables)
]


def _serialize_variables(v: list[WorkflowVariable]) -> dict[str, str | list[str]]:
    """Serialize a list of workflow variables to a string for use in templating.

    Examples:

    ```python
    >>> _serialize_variables([TaskIdVariable(value="task1", suffix="return")])
    {'asstr': 'task1', 'aslist': ['task1']}
    >>> _serialize_variables([EnvVariable(value="ENV_VAR")])
    {'asstr': 'os.environ["ENV_VAR"]', 'aslist': ['os.environ["ENV_VAR"]']}
    >>> _serialize_variables([TaskIdVariable(value="task1", suffix="return"), TaskIdVariable(value="task2", suffix="return")])
    {'asstr': '[task1, task2]', 'aslist': ['task1', 'task2']}
    >>> _serialize_variables([TaskIdVariable(value="task1", suffix="return"), EnvVariable(value="ENV_VAR")])
    {'asstr': '[task1, os.environ["ENV_VAR"]]', 'aslist': ['task1', 'os.environ["ENV_VAR"]']}

    ```

    """
    return {
        "asstr": (
            v[0].model_dump()
            if len(v) == 1
            else f"[{', '.join(var.model_dump() for var in v)}]"
        ),
        "aslist": [var.model_dump() for var in v],
    }


def _singleton_or_list_aslist(s: T | list[T]) -> list[T]:
    return [s] if not isinstance(s, list) else s


Vars = Annotated[
    list[WorkflowVariable],
    BeforeValidator(_singleton_or_list_aslist),
    PlainSerializer(_serialize_variables, return_type=dict[str, str | list[str]]),
]
TaskInstanceId = Annotated[
    str,
    AfterValidator(_is_not_reserved),
    AfterValidator(_is_valid_task_instance_id),
]
KnownTaskName = Annotated[str, AfterValidator(_is_known_task_name)]
KnownTaskArgName = Annotated[str, AfterValidator(_is_identifier)]
ArgDependencies: TypeAlias = dict[KnownTaskArgName, Vars]
SpecId = Annotated[
    str, AfterValidator(_is_not_reserved), AfterValidator(_is_valid_spec_name)
]
ParallelOpArgNames = Annotated[
    list[KnownTaskArgName], BeforeValidator(_singleton_or_list_aslist)
]


class _ParallelOperation(_ForbidExtra):
    argnames: ParallelOpArgNames = Field(default_factory=list)
    argvalues: Vars = Field(default_factory=list)

    @model_validator(mode="after")
    def both_fields_required_if_either_given(self) -> "_ParallelOperation":
        if bool(self.argnames) != bool(self.argvalues):
            raise ValueError(
                "Both `argnames` and `argvalues` must be provided if either is given."
            )
        return self

    def __bool__(self):
        """Return False if both `argnames` and `argvalues` are empty. Otherwise, return True.
        Lets us use empty `_ParallelOperation` models as their own defaults in `TaskInstance`,
        while still allowing boolean checks such as `if self.map`, `if self.mapvalues`, etc.
        """
        return bool(self.argnames) and bool(self.argvalues)

    @property
    def all_dependencies_dict(self) -> dict[str, list[str]]:
        return {
            arg: [
                var.value for var in self.argvalues if isinstance(var, TaskIdVariable)
            ]
            for arg in self.argnames
        }


class MapOperation(_ParallelOperation):
    pass


class MapValuesOperation(_ParallelOperation):
    @field_validator("argnames")
    def check_argnames(cls, v: str | list) -> str | list:
        if isinstance(v, list) and len(v) > 1:
            raise NotImplementedError(
                "Unpacking mutiple `argnames` is not yet implemented for `mapvalues`."
            )
        return v


class TaskInstance(_ForbidExtra):
    """A task instance in a workflow."""

    name: str = Field(
        description="""\
        A human-readable name, e.g. 'Draw Ecomaps for Each Input Geodataframe'.
        """,
    )
    id: TaskInstanceId = Field(
        description="""\
        Unique identifier for this task instance. This will be used as the name to which
        the result of this task is assigned in the compiled DAG. As such, it should be a
        valid python identifier and it cannot collide with any: Python keywords, Python
        builtins, or any registered known task names. It must also be unique within the
        context of all task instance `id`s in the workflow. The maximum length is 32 chars.
        """,
    )
    known_task_name: KnownTaskName = Field(
        alias="task",
        description="""\
        The name of the known task to be executed. This must be a registered known task name.
        """,
    )
    partial: ArgDependencies = Field(
        default_factory=dict,
        description="""\
        Static keyword arguments to be passed to every invocation of the the task. This is a
        dict with keys which are the names of the arguments on the known task, and values which
        are the values to be passed. The values can be variable references or lists of variable
        references. The variable reference(s) may be in the form `${{ workflow.<task_id>.return }}`
        for task return values, or `${{ env.<ENV_VAR_NAME> }}` for environment variables.

        For more details, see `Task.partial` in the `decorators` module.
        """,
    )
    map: MapOperation = Field(
        default_factory=MapOperation,
        description="""\
        A `map` operation to apply the task to an iterable of values. The `argnames` must be a
        single string, or a list of strings, which correspond to name(s) of argument(s) in the
        task function signature. The `argvalues` must be a variable reference of form
        `${{ workflow.<task_id>.return }}` (where the task id is the id of another task in the
        workflow with an iterable return), or a list of such references (where each reference is
        non-iterable, such that the combination of those references is a flat iterable).

        For more details, see `Task.map` in the `decorators` module.
        """,
    )
    mapvalues: MapValuesOperation = Field(
        default_factory=MapValuesOperation,
        description="""\
        A `mapvalues` operation to apply the task to an iterable of key-value pairs. The `argnames`
        must be a single string, or a single-element list of strings, which correspond to the name
        of an argument on the task function signature. The `argvalues` must be a list of tuples where
        the first element of each tuple is the key to passthrough, and the second element is the value
        to transform.

        For more details, see `Task.mapvalues` in the `decorators` module.
        """,
    )

    @property
    def flattened_partial_values(self) -> list[WorkflowVariable]:
        return [var for dep in self.partial.values() for var in dep]

    @property
    def all_dependencies(self) -> list[WorkflowVariable]:
        return (
            self.flattened_partial_values
            + self.map.argvalues
            + self.mapvalues.argvalues
        )

    @property
    def all_dependencies_dict(self) -> dict[str, list[str]]:
        return (
            {
                arg: [var.value for var in dep if isinstance(var, TaskIdVariable)]
                for arg, dep in self.partial.items()
            }
            | self.map.all_dependencies_dict
            | self.mapvalues.all_dependencies_dict
        )

    @model_validator(mode="after")  # type: ignore[misc]
    def check_does_not_depend_on_self(self) -> "Spec":
        for dep in self.all_dependencies:
            if isinstance(dep, TaskIdVariable) and dep.value == self.id:
                raise ValueError(
                    f"Task `{self.name}` has an arg dependency that references itself: "
                    f"`{dep.value}`. Task instances cannot depend on their own return values."
                )
        return self

    @model_validator(mode="after")  # type: ignore[misc]
    def check_only_oneof_map_or_mapvalues(self) -> "Spec":
        if self.map and self.mapvalues:
            raise ValueError(
                f"Task `{self.name}` cannot have both `map` and `mapvalues` set. "
                "Please choose one or the other."
            )
        return self

    @computed_field  # type: ignore[misc]
    @property
    def known_task(self) -> KnownTask:
        kt = known_tasks[self.known_task_name]
        assert self.known_task_name == kt.function
        return kt

    @computed_field  # type: ignore[misc]
    @property
    def method(self) -> str:
        return (
            "map"
            if self.map
            else None or "mapvalues"
            if self.mapvalues
            else None or "call"
        )


def ruff_formatted(returns_str_func: Callable[..., str]) -> Callable:
    """Decorator to format the output of a function that returns a string with ruff."""

    @functools.wraps(returns_str_func)
    def wrapper(*args, **kwargs):
        unformatted = returns_str_func(*args, **kwargs)
        # https://github.com/astral-sh/ruff/issues/8401#issuecomment-1788806462
        formatted = subprocess.check_output(
            [sys.executable, "-m", "ruff", "format", "-s", "-"],
            input=unformatted,
            encoding="utf-8",
        )
        linted = subprocess.check_output(
            [sys.executable, "-m", "ruff", "check", "--fix", "--exit-zero", "-s", "-"],
            input=formatted,
            encoding="utf-8",
        )
        return linted

    return wrapper


class Spec(_ForbidExtra):
    id: SpecId = Field(
        description="""\
        A unique identifier for this workflow. This will be used to identify the compiled DAG.
        It should be a valid python identifier and cannot collide with any: Python identifiers,
        Python keywords, or Python builtins. The maximum length is 64 chars.
        """
    )
    workflow: list[TaskInstance] = Field(
        description="A list of task instances that define the workflow.",
    )

    @property
    def all_task_ids(self) -> dict[str, str]:
        return {task_instance.name: task_instance.id for task_instance in self.workflow}

    @model_validator(mode="after")
    def check_task_ids_dont_collide_with_spec_id(self) -> "Spec":
        if self.id in self.all_task_ids.values():
            name = next(name for name, id in self.all_task_ids.items() if id == self.id)
            raise ValueError(
                "Task `id`s cannot be the same as the spec `id`. "
                f"The `id` of task `{name}` is `{self.id}`, which is the same as the spec `id`. "
                "Please choose a different `id` for this task."
            )
        return self

    @model_validator(mode="after")
    def check_task_ids_unique(self) -> "Spec":
        if len(self.all_task_ids.values()) != len(set(self.all_task_ids.values())):
            id_keyed_dict: dict[str, list[str]] = {
                id: [] for id in self.all_task_ids.values()
            }
            for name, id in self.all_task_ids.items():
                id_keyed_dict[id].append(name)
            dupes = {id: names for id, names in id_keyed_dict.items() if len(names) > 1}
            dupes_fmt_string = "; ".join(
                f"{id=} is shared by {names}" for id, names in dupes.items()
            )
            raise ValueError(
                "All task instance `id`s must be unique in the workflow. "
                f"Found duplicate ids: {dupes_fmt_string}"
            )
        return self

    @model_validator(mode="after")
    def check_all_task_id_deps_use_actual_ids_of_other_tasks(self) -> "Spec":
        all_ids = [task_instance.id for task_instance in self.workflow]
        for ti_id, deps in self.task_instance_dependencies.items():
            for d in deps:
                if d not in all_ids:
                    raise ValueError(
                        f"Task `{ti_id}` has an arg dependency `{d}` that is "
                        f"not a valid task id. Valid task ids for this workflow are: {all_ids}"
                    )
        return self

    @computed_field  # type: ignore[misc]
    @property
    def task_instance_dependencies(self) -> dict[str, list[str]]:
        return {
            task_instance.id: [
                d.value
                for d in task_instance.all_dependencies
                if isinstance(d, TaskIdVariable)
            ]
            for task_instance in self.workflow
        }

    @model_validator(mode="after")
    def check_task_instances_are_in_topological_order(self) -> "Spec":
        seen_task_instance_ids = set()
        for task_instance_id, deps in self.task_instance_dependencies.items():
            seen_task_instance_ids.add(task_instance_id)
            for dep_id in deps:
                if dep_id not in seen_task_instance_ids:
                    dep_name = next(ti.name for ti in self.workflow if ti.id == dep_id)
                    task_instance_name = next(
                        ti.name for ti in self.workflow if ti.id == task_instance_id
                    )
                    raise ValueError(
                        f"Task instances are not in topological order. "
                        f"`{task_instance_name}` depends on `{dep_name}`, "
                        f"but `{dep_name}` is defined after `{task_instance_name}`."
                    )
        return self


class DagCompiler(BaseModel):
    spec: Spec

    # jinja kwargs; TODO: nest in separate model
    template: str = "script-sequential.jinja2"
    template_dir: pathlib.Path = TEMPLATES

    # compilation settings
    testing: bool = False
    mock_tasks: list[str] = Field(default_factory=list)

    def get_dag_config(self) -> dict:
        if self.mock_tasks and not self.testing:
            raise ValueError(
                "If you provide mocks, you must set `testing=True` to use them."
            )
        dag_config = self.model_dump(
            exclude={"template", "template_dir"},
            context={
                "testing": self.testing,
                "mocks": self.mock_tasks,
            },
        )
        if self.template == "jupytext.jinja2":
            dag_config |= {
                "per_taskinstance_params_notebook": self.get_per_taskinstance_params_notebook(),
            }
        return dag_config

    @property
    def per_taskinstance_omit_args(
        self,
    ) -> dict[TaskInstanceId, list[KnownTaskArgName]]:
        """For a given arg on a task instance, if it is dependent on another task's return
        value, we omit it from the user-facing parameters, so that it's not set twice (once
        as a dependency in the spec, and a second time by the user via the parameter form).
        """
        return {
            t.id: (
                ["return"]
                + [arg for arg in t.partial]
                + [arg for arg in t.map.argnames]
                + [arg for arg in t.mapvalues.argnames]
            )
            for t in self.spec.workflow
        }

    def get_params_jsonschema(self) -> dict[str, Any]:
        properties = {
            t.name: t.known_task.parameters_jsonschema(
                omit_args=self.per_taskinstance_omit_args.get(t.id, []),
            )
            for t in self.spec.workflow
        }

        definitions = {}
        for _, schema in properties.items():
            if "$defs" in schema:
                definitions.update(schema["$defs"])
                del schema["$defs"]

        react_json_schema_form = ReactJSONSchemaFormConfiguration(properties=properties)
        react_json_schema_form.definitions = definitions
        return react_json_schema_form.model_dump(by_alias=True)

    def get_params_fillable_yaml(self) -> str:
        yaml_str = ""
        for t in self.spec.workflow:
            yaml_str += t.known_task.parameters_annotation_yaml_str(
                title=t.id,
                description=f"# Parameters for '{t.name}' using task `{t.known_task_name}`.",
                omit_args=self.per_taskinstance_omit_args.get(t.id, []),
            )
        return yaml_str

    def get_per_taskinstance_params_notebook(self) -> dict[str, str]:
        return {
            t.id: t.known_task.parameters_notebook(
                omit_args=self.per_taskinstance_omit_args.get(t.id, []),
            )
            for t in self.spec.workflow
        }

    @ruff_formatted
    def generate_dag(self) -> str:
        env = Environment(loader=FileSystemLoader(self.template_dir))
        template = env.get_template(self.template)
        return template.render(self.get_dag_config())
