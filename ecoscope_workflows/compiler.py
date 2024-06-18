import copy
import functools
import pathlib
import subprocess
from typing import Any, Callable

import pandera as pa
from jinja2 import Environment, FileSystemLoader
from pydantic import (
    BaseModel,
    Field,
    FieldSerializationInfo,
    computed_field,
    field_serializer,
)

from ecoscope_workflows.registry import KnownTask, known_deserializers, known_tasks
from ecoscope_workflows.annotations import is_subscripted_pandera_dataframe


TEMPLATES = pathlib.Path(__file__).parent / "templates"


class TasksSpec(BaseModel):
    tasks: dict[str, dict[str, str]]
    # TODO: pydantic validator for `self.tasks`, as follows:
    #  - all outer dict keys must be registered `known_tasks`
    #  - all inner dict keys must be argument names on the known task they are nested under
    #  - all inner dict values must be names of other known tasks in the spec
    #  - there cannot be any cycle errors


class TaskInstance(BaseModel):
    known_task_name: str  # TODO: validate is valid key in known_tasks
    arg_dependencies: dict = Field(default_factory=dict)
    # TODO: something about defaulting to registered deserializers
    # by arg type (via introspection); just manual for now
    arg_prevalidators: dict = Field(default_factory=dict)
    return_postvalidator: Callable | None = None

    @computed_field  # type: ignore[misc]
    @property
    def known_task(self) -> KnownTask:
        kt = known_tasks[self.known_task_name]
        assert self.known_task_name == kt.function
        return kt

    @field_serializer("arg_prevalidators")
    def serialize_arg_prevalidators(self, v: Any, info: FieldSerializationInfo):
        context: dict = info.context
        if context:
            pass
        return {
            arg_name: func.__name__ for arg_name, func in self.arg_prevalidators.items()
        }


def ruff_formatted(returns_str_func: Callable[..., str]) -> Callable:
    """Decorator to format the output of a function that returns a string with ruff."""

    @functools.wraps(returns_str_func)
    def wrapper(*args, **kwargs):
        unformatted = returns_str_func(*args, **kwargs)
        # https://github.com/astral-sh/ruff/issues/8401#issuecomment-1788806462
        cmd = ["ruff", "format", "-"]
        formatted = subprocess.check_output(cmd, input=unformatted, encoding="utf-8")
        return formatted

    return wrapper


class DagCompiler(BaseModel):
    name: str  # TODO: needs to be a valid python identifier
    tasks: list[TaskInstance]
    cache_root: str  # e.g. "gcs://my-bucket/dag-runs/cache/"

    # @dag kwargs; TODO: nest in separate model
    schedule: str | None = None  # TODO: Literal of valid strings
    start_date: str = "datetime(2021, 12, 1)"
    catchup: bool = False

    # jinja kwargs; TODO: nest in separate model
    template: str = "airflow-kubernetes.jinja2"
    template_dir: pathlib.Path = TEMPLATES

    # compilation settings
    testing: bool = False
    mock_tasks: list[str] = Field(default_factory=list)
    # TODO: on __init__ (or in cached_property), sort tasks
    # topologically so we know what order to invoke them in dag

    @classmethod
    def from_spec(cls, spec: dict) -> "DagCompiler":
        non_task_kws = copy.deepcopy(spec)
        del non_task_kws["tasks"]
        tasks_spec = TasksSpec(**spec)
        tasks = []
        for task_name in tasks_spec.tasks:
            arg_dependencies: dict[str, str] = {}
            arg_prevalidators: dict[str, Callable] = {}
            # if the value of the task is None, the task has no dependencies
            if tasks_spec.tasks[task_name]:
                # if the value is a dict, then then that dict's k:v pairs are the
                # arg on the task mapped to the dependency to deserialize it from
                for arg, dep in tasks_spec.tasks[task_name].items():
                    arg_dependencies |= {arg: f"{dep}_return"}
                    # now we have to figure out how to deserialize this arg when passed
                    # FIXME: this factoring seems sub-optimal; ideally we only introspect the
                    # signature (which triggers import, and might be slow) once per compilation.
                    arg_type = known_tasks[task_name].params_annotations_args[arg][0]
                    if is_subscripted_pandera_dataframe(arg_type):
                        # NOTE: even if an argument is passed as as an `arg_dependency`, we don't need a
                        # pre-validator unless the value passed needs some custom logic for deserialization
                        # (e.g. being loaded from a storage device, etc.). For just strings that Pydantic
                        # will know how to parse in built-in/obvious ways, this is not needed.
                        arg_prevalidators |= {
                            arg: known_deserializers[pa.typing.DataFrame]
                        }
                        # TODO: right now the only custom type we're handling is the dataframe, let's add others soon!
            tasks.append(
                TaskInstance(
                    known_task_name=task_name,
                    arg_dependencies=arg_dependencies,
                    arg_prevalidators=arg_prevalidators,
                )
            )
        return cls(tasks=tasks, **non_task_kws)

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
        return ["return"] + [arg for t in self.tasks for arg in t.arg_dependencies]

    def get_params_jsonschema(self) -> dict[str, dict]:
        return {
            t.known_task_name: t.known_task.parameters_jsonschema(
                omit_args=self._omit_args
            )
            for t in self.tasks
        }

    def get_params_fillable_yaml(self) -> str:
        yaml_str = ""
        for t in self.tasks:
            yaml_str += t.known_task.parameters_annotation_yaml_str(
                omit_args=self._omit_args
            )
        return yaml_str

    def get_connections(self) -> dict:
        return {
            t.known_task_name: t.known_task.connections_model_fields
            for t in self.tasks
            if t.known_task.connections_model_fields
        }

    def get_connections_model_fields(self) -> dict:
        return {
            t.known_task_name: t.known_task.connections_model_fields
            for t in self.tasks
            if t.known_task.connections_model_fields
        }

    @ruff_formatted
    def generate_dag(self) -> str:
        env = Environment(loader=FileSystemLoader(self.template_dir))
        template = env.get_template(self.template)
        return template.render(self.dag_config)
