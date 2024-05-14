import yaml
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("."))
template = env.get_template("dag.jinja2")

with open("dag.yaml") as f:
    config = yaml.safe_load(f)

rendered_template = template.render(config)

with open("_dag.py", "w") as f:
    f.write(rendered_template)
