import functools
import pathlib
import subprocess
from typing import Callable

from jinja2 import Environment, FileSystemLoader
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
)

from ecoscope_workflows.registry import KnownTask, known_tasks


TEMPLATES = pathlib.Path(__file__).parent / "templates"


class _ForbidExtra(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TaskInstance(_ForbidExtra):
    known_task_name: str = Field(
        alias="task"
    )  # TODO: validate is valid key in known_tasks
    arg_dependencies: dict = Field(default_factory=dict, alias="with")

    @computed_field  # type: ignore[misc]
    @property
    def known_task(self) -> KnownTask:
        kt = known_tasks[self.known_task_name]
        assert self.known_task_name == kt.function
        return kt

    @field_serializer("arg_dependencies")
    def serialize_arg_deps(self, deps: dict, _info):
        # TODO: require `.return_value` suffix on all return values
        # TODO: require deps to be wrapped in ${} for for clarity
        return {arg: f"{dep}_return" for arg, dep in deps.items()}


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


class Spec(_ForbidExtra):
    name: str  # TODO: needs to be a valid python identifier
    cache_root: str  # e.g. "gcs://my-bucket/dag-runs/cache/"
    workflow: list[TaskInstance]
    # TODO: pydantic validator for `self.workflow`, as follows:
    #  - all outer dict keys must be registered `known_tasks`
    #  - all inner dict keys must be argument names on the known task they are nested under
    #  - all inner dict values must be names of other known tasks in the spec
    #  - there cannot be any cycle errors

    # TODO: on __init__ (or in cached_property), sort tasks
    # topologically so we know what order to invoke them in dag


class DagCompiler(BaseModel):
    spec: Spec

    # jinja kwargs; TODO: nest in separate model
    template: str = "airflow-kubernetes.jinja2"
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
        return ["return"] + [
            arg for t in self.spec.workflow for arg in t.arg_dependencies
        ]

    def get_params_jsonschema(self) -> dict[str, dict]:
        return {
            t.known_task_name: t.known_task.parameters_jsonschema(
                omit_args=self._omit_args
            )
            for t in self.spec.workflow
        }

    def get_params_fillable_yaml(self) -> str:
        yaml_str = ""
        for t in self.spec.workflow:
            yaml_str += t.known_task.parameters_annotation_yaml_str(
                omit_args=self._omit_args
            )
        return yaml_str

    @ruff_formatted
    def generate_dag(self) -> str:
        env = Environment(loader=FileSystemLoader(self.template_dir))
        template = env.get_template(self.template)
        return template.render(self.dag_config)
