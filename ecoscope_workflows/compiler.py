import copy
import pathlib
from typing import Callable

import pandera as pa
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field, computed_field

from ecoscope_workflows.registry import KnownTask, known_deserializers, known_tasks
from ecoscope_workflows.types import is_subscripted_pandera_dataframe


TEMPLATES = pathlib.Path(__file__).parent / "templates"


class TasksSpec(BaseModel):
    tasks: dict[str, dict[str, str] | None]


class TaskInstance(BaseModel):
    known_task_name: str  # TODO: validate is valid key in known_tasks
    arg_dependencies: dict = Field(default_factory=dict)
    # TODO: something about defaulting to registered deserializers
    # by arg type (via introspection); just manual for now
    arg_prevalidators: dict = Field(default_factory=dict)
    return_postvalidator: Callable | None = None

    @computed_field
    @property
    def known_task(self) -> KnownTask:
        kt = known_tasks[self.known_task_name]
        assert self.known_task_name == kt.function
        return kt

    def validate_argprevalidators(self):
        ...


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
    template_dir: str = TEMPLATES

    # TODO: on __init__ (or in cached_property), sort tasks
    # topologically so we know what order to invoke them in dag

    @classmethod
    def from_spec(cls, spec: dict) -> "DagCompiler":
        non_task_kws = copy.deepcopy(spec)
        del non_task_kws["tasks"]
        tasks_spec = TasksSpec(**spec)
        tasks = []
        for task_name in tasks_spec.tasks:
            arg_dependencies = {}
            arg_prevalidators = {}
            # if the value of the task is None, the task has no dependencies
            if tasks_spec.tasks[task_name] is not None:
                # if the value is a dict, then then that dict's k:v pairs are the
                # arg on the task mapped to the dependency to deserialize it from
                for arg, dep in tasks_spec.tasks[task_name].items():
                    arg_dependencies |= {arg: f"{dep}_return"}
                    # now we have to figure out how to deserialize this arg when passed
                    # FIXME: this factoring seems sub-optimal; ideally we only introspect the
                    # signature (which triggers import, and might be slow) once per compilation.
                    kt = known_tasks[task_name]
                    arg_type = kt.parameters_annotation[arg][0]
                    # FIXME: this logic possibly clearer as a computed_field on the KnownTask model?
                    if is_subscripted_pandera_dataframe(arg_type):
                        arg_type = pa.typing.DataFrame
                    arg_prevalidators |= {arg: known_deserializers[arg_type]}
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
        return self.model_dump(exclude={"template", "template_dir"})
    
    def dag_params_schema(self) -> dict[str, dict]:
        return {t.known_task_name: t.known_task.parameters_jsonschema() for t in self.tasks}
    
    def dag_params_yaml(self) -> str:
        yaml_str = ""
        for t in self.tasks:
            yaml_str += t.known_task.parameters_annotation_yaml_str()
        return yaml_str

    def _generate_dag(self) -> str:
        env = Environment(loader=FileSystemLoader(self.template_dir))
        template = env.get_template(self.template)
        return template.render(self.dag_config)

    def generate(self):
        params = self._get_params_schema()
        dag = self._generate_dag()
