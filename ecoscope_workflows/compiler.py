import builtins
import functools
import keyword
import pathlib
import subprocess
from typing import Annotated, Callable, Literal, TypeAlias

from jinja2 import Environment, FileSystemLoader
from pydantic import (
    BaseModel,
    ConfigDict,
    PlainSerializer,
    Field,
    computed_field,
    model_serializer,
    model_validator,
)
from pydantic.functional_validators import AfterValidator, BeforeValidator

from ecoscope_workflows.registry import KnownTask, known_tasks


TEMPLATES = pathlib.Path(__file__).parent / "templates"


class _ForbidExtra(BaseModel):
    model_config = ConfigDict(extra="forbid")


class WorkflowVariableBase(BaseModel):
    """Base class for workflow variables."""

    value: str


class TaskIdVariable(WorkflowVariableBase):
    """A variable that references the return value of another task in the workflow."""

    suffix: Literal["return"]

    @model_serializer
    def serialize(self) -> str:
        return self.value


class EnvVariable(WorkflowVariableBase):
    """A variable that references an environment variable."""

    @model_serializer
    def serialize(self) -> str:
        return f'os.environ["{self.value}"]'


def _parse_variable(s: str) -> str:
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


def _parse_variables(s: str | list[str]) -> str | list[str]:
    if isinstance(s, str):
        return _parse_variable(s)
    return [_parse_variable(v) for v in s]


def _is_not_reserved(s: str):
    if not s.isidentifier():
        raise ValueError(f"`{s}` is not a valid python identifier.")
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


Variable = Annotated[TaskIdVariable | EnvVariable, BeforeValidator(_parse_variables)]
TaskInstanceId = Annotated[
    str,
    AfterValidator(_is_not_reserved),
    AfterValidator(_is_valid_task_instance_id),
]
KnownTaskName = Annotated[str, AfterValidator(_is_known_task_name)]
KnownTaskArgName: TypeAlias = str
_ArgDependenciesTypeAlias: TypeAlias = dict[KnownTaskArgName, Variable | list[Variable]]


def _serialize_arg_deps(arg_deps: _ArgDependenciesTypeAlias) -> dict[str, str]:
    return {
        arg: (
            dep.model_dump()
            if not isinstance(dep, list)
            else f"[{', '.join(d.model_dump() for d in dep)}]"
        )
        for arg, dep in arg_deps.items()
    }


ArgDependencies = Annotated[
    _ArgDependenciesTypeAlias,
    PlainSerializer(_serialize_arg_deps, return_type=dict[str, str]),
]
SpecName = Annotated[
    str, AfterValidator(_is_not_reserved), AfterValidator(_is_valid_spec_name)
]


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
    mode: Literal["call", "map"] = Field(
        default="call",
        description="""\
        The mode in which this task will be executed. In `call` mode, the task will be
        called directly. In `map` mode, the task will be called in parallel for each
        element of an iterable. The iterable is the return value of the task specified
        in the `with` field.
        """,
    )
    map_iterable: ArgDependencies = Field(
        default_factory=dict,
        alias="iter",
        description="""\
        The iterable to be passed to the task in `map` mode. This must be a single key-value
        pair where the key is the name of the argument on the known task that will receive
        each element of the iterable, and the value is the iterable itself. The value can be
        a variable reference or a list of variable references. The variable reference(s) must be
        in the form `${{ workflow.<task_id>.return }}` where `<task_id>` is the `id` of another
        task instance in the workflow.
        """,
    )
    arg_dependencies: ArgDependencies = Field(
        default_factory=dict,
        alias="with",
        description="""\
        Keyword arguments to be passed to the task. This must be a dictionary where the keys
        are the names of the arguments on the known task that will receive the values, and the
        values are the values to be passed. The values can be variable references or lists of
        variable references. The variable reference(s) may be in the form
        `${{ workflow.<task_id>.return }}` for task return values, or `${{ env.<ENV_VAR_NAME> }}`
        for environment variables. In mode `map` these keyword arguments will be passed to each
        invocation of the task.
        """,
    )

    @model_validator(mode="after")
    def check_map_iterable(self) -> "Spec":
        if self.mode == "call" and self.map_iterable:
            raise ValueError(
                "In `call` mode, the `iter` field must be empty. "
                "Specify keyword arguments in the `with` field."
            )
        elif self.mode == "map" and not self.map_iterable:
            raise ValueError(
                "In `map` mode, the `iter` field must be specified with an iterable."
            )
        if len(self.map_iterable) > 1:
            raise ValueError(
                "The `iter` field must have only one key-value pair. "
                "To pass additional keyword arguments to each mapped invocation, "
                "provide them in the `with` field."
            )
        return self

    @computed_field  # type: ignore[misc]
    @property
    def known_task(self) -> KnownTask:
        kt = known_tasks[self.known_task_name]
        assert self.known_task_name == kt.function
        return kt


def ruff_formatted(returns_str_func: Callable[..., str]) -> Callable:
    """Decorator to format the output of a function that returns a string with ruff."""

    @functools.wraps(returns_str_func)
    def wrapper(*args, **kwargs):
        unformatted = returns_str_func(*args, **kwargs)
        # https://github.com/astral-sh/ruff/issues/8401#issuecomment-1788806462
        formatted = subprocess.check_output(
            ["ruff", "format", "-s", "-"],
            input=unformatted,
            encoding="utf-8",
        )
        linted = subprocess.check_output(
            ["ruff", "check", "--fix", "--exit-zero", "-s", "-"],
            input=formatted,
            encoding="utf-8",
        )
        return linted

    return wrapper


class Spec(_ForbidExtra):
    name: SpecName = Field(
        description="""\
        A unique name for this workflow. This will be used as the name of the compiled DAG.
        It should be a valid python identifier and cannot collide with any: Python identifiers,
        Python keywords, or Python builtins. The maximum length is 64 chars.
        """
    )
    workflow: list[TaskInstance] = Field(
        description="A list of task instances that define the workflow.",
    )

    @model_validator(mode="after")
    def check_task_ids_unique(self) -> "Spec":
        all_ids = {
            task_instance.name: task_instance.id for task_instance in self.workflow
        }
        if len(all_ids.values()) != len(set(all_ids.values())):
            id_keyed_dict: dict[str, list[str]] = {id: [] for id in all_ids.values()}
            for name, id in all_ids.items():
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
    def check_all_arg_deps_are_ids_of_other_tasks(self) -> "Spec":
        all_ids = [task_instance.id for task_instance in self.workflow]
        for task_instance in self.workflow:
            for dep in task_instance.arg_dependencies.values():
                # deps could be `Variable` or `list[Variable]` (i.e. `str` or `list[str]`),
                # so we cast to list if the former, to handle validation in a uniform way
                dep_list = [d for d in dep] if isinstance(dep, list) else [dep]
                for d in dep_list:
                    if isinstance(d, TaskIdVariable) and d.value not in all_ids:
                        raise ValueError(
                            f"Task `{task_instance.name}` has an arg dependency `{d.value}` that is "
                            f"not a valid task id. Valid task ids for this workflow are: {all_ids}"
                        )
        return self

    # TODO: on __init__ (or in cached_property), sort tasks
    # topologically so we know what order to invoke them in dag


class DagCompiler(BaseModel):
    spec: Spec

    # jinja kwargs; TODO: nest in separate model
    template: str = "script-sequential.jinja2"
    template_dir: pathlib.Path = TEMPLATES

    # compilation settings
    testing: bool = False
    mock_tasks: list[str] = Field(default_factory=list)

    @property
    def dag_config(self) -> dict:
        if self.mock_tasks and not self.testing:
            raise ValueError(
                "If you provide mocks, you must set `testing=True` to use them."
            )
        return self.model_dump(
            exclude={"template", "template_dir"},
            context={
                "testing": self.testing,
                "mocks": self.mock_tasks,
                "omit_args": self._omit_args,
            },
        )

    @property
    def _omit_args(self) -> list[str]:
        # for a given task arg, if it is dependent on another task's return value,
        # we don't need to include it in the `dag_params_schema`,
        # because we don't need it to be passed as a parameter by the user.
        return (
            ["return"]
            + [arg for t in self.spec.workflow for arg in t.arg_dependencies]
            + [arg for t in self.spec.workflow for arg in t.map_iterable]
        )

    def get_params_jsonschema(self) -> dict[str, dict]:
        return {
            t.id: t.known_task.parameters_jsonschema(omit_args=self._omit_args)
            for t in self.spec.workflow
        }

    def get_params_fillable_yaml(self) -> str:
        yaml_str = ""
        for t in self.spec.workflow:
            yaml_str += t.known_task.parameters_annotation_yaml_str(
                title=t.id,
                description=f"# Parameters for '{t.name}' using task `{t.known_task_name}`.",
                omit_args=self._omit_args,
            )
        return yaml_str

    @ruff_formatted
    def generate_dag(self) -> str:
        env = Environment(loader=FileSystemLoader(self.template_dir))
        template = env.get_template(self.template)
        return template.render(self.dag_config)
