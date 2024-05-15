import pathlib
from typing import Annotated, Callable

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator

from ecoscope_workflows.registry import KnownTask, known_tasks

TEMPLATES = pathlib.Path(__file__).parent / "templates"


class TaskInstance(BaseModel):
    known_task: Annotated[KnownTask, BeforeValidator(lambda name: known_tasks[name])]
    dependencies: list[str] = Field(default_factory=list)
    arg_prevalidators: dict = Field(default_factory=dict)
    return_postvalidator: Callable | None = None

    def validate_argprevalidators(self):
        ...


class DagBuilder(BaseModel):
    name: str
    tasks: list[TaskInstance]
    template: str = "kubernetes.jinja2"
    template_dir: str = TEMPLATES

    # TODO: on __init__ (or in cached_property), sort tasks
    # topologically so we know what order to invoke them in dag

    def _get_params_schema(self):
        ...

    def _generate_dag(self) -> str:
        env = Environment(loader=FileSystemLoader(self.template_dir))
        template = env.get_template(self.template)

        config = self.model_dump(exclude={"template", "template_dir"})
        return template.render(config)

    def generate(self):
        params = self._get_params_schema()
        dag = self._generate_dag()
