import builtins
import functools
import keyword
import pathlib
import subprocess
from typing import Annotated, Callable, TypeAlias

from jinja2 import Environment, FileSystemLoader
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    model_validator,
)
from pydantic.functional_validators import AfterValidator

from ecoscope_workflows.registry import KnownTask, known_tasks


TEMPLATES = pathlib.Path(__file__).parent / "templates"


class _ForbidExtra(BaseModel):
    model_config = ConfigDict(extra="forbid")


def _parse_variable(s: str):
    assert s.startswith("${{") and s.endswith("}}")
    drop_curlies = s.replace("${{", "").replace("}}", "").strip()
    assert drop_curlies.count(".") == 1
    assert drop_curlies.endswith(".return")  # TODO: add other options, like [*]
    return drop_curlies.split(".")[0]


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


# TODO: structural Variable options `[*]` etc. for iterables
Variable = Annotated[str, AfterValidator(_parse_variable)]
TaskInstanceId = Annotated[
    str,
    AfterValidator(_is_not_reserved),
    AfterValidator(_is_valid_task_instance_id),
]
KnownTaskName = Annotated[str, AfterValidator(_is_known_task_name)]
KnownTaskArgName: TypeAlias = str

SpecName = Annotated[
    str, AfterValidator(_is_not_reserved), AfterValidator(_is_valid_spec_name)
]


class TaskInstance(_ForbidExtra):
    """A task instance in a workflow."""

    name: str
    id: TaskInstanceId = Field(
        description="""\
        Unique identifier for this task instance. This will be used as the name to which
        the result of this task is assigned in the compiled DAG. As such, it should be a
        valid python identifier and it cannot collide with any: Python keywords, Python
        builtins, or any registered known task names. It must also be unique within the
        context of all task instance `id`s in the workflow. The maximum length is 32 chars.
        """
    )
    known_task_name: KnownTaskName = Field(alias="task")
    arg_dependencies: dict[KnownTaskArgName, Variable] = Field(
        default_factory=dict, alias="with"
    )

    @computed_field  # type: ignore[misc]
    @property
    def known_task(self) -> KnownTask:
        kt = known_tasks[self.known_task_name]
        assert self.known_task_name == kt.function
        return kt

    # TODO: this requires parsing known task parameter names at registration time (or in DistributedTask)
    # @model_validator(mode="after")
    # def check_known_task_arg_names(self) -> "TaskInstance":
    #     for arg in self.arg_dependencies:
    #         if arg not in self.known_task.parameters:
    #             raise ValueError(
    #                 f"`{arg}` is not a valid argument name for task `{self.known_task_name}`."
    #             )
    #     return self


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
    name: SpecName = Field(
        description="""\
        A unique name for this workflow. This will be used as the name of the compiled DAG.
        It should be a valid python identifier and cannot collide with any: Python identifiers,
        Python keywords, or Python builtins. The maximum length is 64 chars.
        """
    )
    cache_root: str  # e.g. "gcs://my-bucket/dag-runs/cache/"
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
                if dep not in all_ids:
                    raise ValueError(
                        f"Task `{task_instance.name}` has an arg dependency `{dep}` that is "
                        f"not a valid task id. Valid task ids for this workflow are: {all_ids}"
                    )
        return self

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
