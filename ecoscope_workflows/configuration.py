import pathlib
from typing import Callable

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel


TEMPLATES = pathlib.Path(__file__).parent / "templates"


class TaskRegistration(BaseModel):
    image: str
    pod_name: str
    task_import: str


class TaskInstance(TaskRegistration):
    dependencies: list[str]
    arg_prevalidators: dict
    return_postvalidator: Callable

    def validate_argprevalidators(self):
        ...


class DagBuilder(BaseModel):
    name: str
    tasks: list[TaskInstance]
    template: str = "kubernetes.jinja2"
    template_dir: str = TEMPLATES

    def generate(self):
        env = Environment(loader=FileSystemLoader(self.template_dir))
        template = env.get_template(self.template)

        # with open("dag.yaml") as f:
        #     config = yaml.safe_load(f)

        config = self.to

        rendered_template = template.render(config)

        with open("_dag.py", "w") as f:
            f.write(rendered_template)
