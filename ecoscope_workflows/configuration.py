import pathlib
from typing import Callable

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field, computed_field

from ecoscope_workflows.registry import KnownTask, known_tasks

TEMPLATES = pathlib.Path(__file__).parent / "templates"


class TaskInstance(BaseModel):
    known_task_name: str  # TODO: validate is valid key in known_tasks
    arg_dependencies: dict = Field(default_factory=dict)
    # TODO: something about defaulting to registered deserializers
    # by arg type (via introspection); just manual for now
    arg_prevalidators: dict = Field(default_factory=dict)
    return_postvalidator: Callable | None = None

    @computed_field
    def known_task(self) -> KnownTask:
        return known_tasks[self.known_task_name]

    def validate_argprevalidators(self):
        ...


class DagBuilder(BaseModel):
    name: str  # TODO: does this need to be a valid python identifier?
    tasks: list[TaskInstance]
    cache_root: str  # e.g. "gcs://my-bucket/dag-runs/cache/" 

    # @dag kwargs; TODO: nest in separate model 
    schedule: str | None = None  # TODO: Literal of valid strings
    start_date: str = "datetime(2021, 12, 1)"
    catchup: bool = False

    # jinja kwargs; TODO: nest in separate model
    template: str = "kubernetes.jinja2"
    template_dir: str = TEMPLATES

    # TODO: on __init__ (or in cached_property), sort tasks
    # topologically so we know what order to invoke them in dag

    @property
    def dag_config(self):
        return self.model_dump(exclude={"template", "template_dir"})
    
    def _get_params_schema(self):
        ...

    def _generate_dag(self) -> str:
        env = Environment(loader=FileSystemLoader(self.template_dir))
        template = env.get_template(self.template)
        return template.render(self.dag_config)

    def generate(self):
        params = self._get_params_schema()
        dag = self._generate_dag()
