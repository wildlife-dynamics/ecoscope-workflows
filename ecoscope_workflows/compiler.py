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
SpecId = Annotated[
    str, AfterValidator(_is_not_reserved), AfterValidator(_is_valid_spec_name)
]


def _dep_as_list(dep: Variable | list[Variable]) -> list[Variable]:
    return [dep] if not isinstance(dep, list) else dep


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
        Keyword arguments to be passed to the task. This must be a dictionary where the keys
        are the names of the arguments on the known task that will receive the values, and the
        values are the values to be passed. The values can be variable references or lists of
        variable references. The variable reference(s) may be in the form
        `${{ workflow.<task_id>.return }}` for task return values, or `${{ env.<ENV_VAR_NAME> }}`
        for environment variables. In mode `map` these keyword arguments will be passed to each
        invocation of the task.
        """,
    )
    map: dict | None = Field(default_factory=dict)
    mapvalues: dict | None = Field(default_factory=dict)

    @model_validator(mode="after")
    def check_does_not_depend_on_self(self) -> "Spec":
        # TODO: check `call`/`map`/`mapvalues` args as well
        for arg, dep in self.partial.items():
            for d in _dep_as_list(dep):
                if isinstance(d, TaskIdVariable) and d.value == self.id:
                    raise ValueError(
                        f"Task `{self.name}` has an arg dependency that references itself: "
                        f"`{arg}` is set to depend on the return value of `{d.value}`. "
                        "Task instances cannot depend on their own return values."
                    )
        return self

    @model_validator(mode="after")
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
    def check_all_partial_args_are_ids_of_other_tasks(self) -> "Spec":
        all_ids = [task_instance.id for task_instance in self.workflow]
        for task_instance in self.workflow:
            for dep in task_instance.partial.values():
                for d in _dep_as_list(dep):
                    if isinstance(d, TaskIdVariable) and d.value not in all_ids:
                        raise ValueError(
                            f"Task `{task_instance.name}` has an arg dependency `{d.value}` that is "
                            f"not a valid task id. Valid task ids for this workflow are: {all_ids}"
                        )
        return self

    @property
    def task_instance_dependencies(self) -> dict[str, list[str]]:
        return {
            task_instance.id: (
                [
                    d.value
                    for dep in task_instance.partial.values()
                    for d in _dep_as_list(dep)
                    if isinstance(d, TaskIdVariable)
                ]
                # TODO: check `call`/`map`/`mapvalues` args as well
            )
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
            ["return"] + [arg for t in self.spec.workflow for arg in t.partial]
            # TODO: check `call`/`map`/`mapvalues` args as well
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
