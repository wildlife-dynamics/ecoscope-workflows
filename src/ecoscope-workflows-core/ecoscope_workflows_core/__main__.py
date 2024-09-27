import hashlib
from io import TextIOWrapper

import click
import ruamel.yaml

from ecoscope_workflows_core.artifacts import (
    Dags,
    PackageDirectory,
    Tests,
    WorkflowArtifacts,
)
from ecoscope_workflows_core.compiler import DagCompiler, Spec
# from ecoscope_workflows_core.visualize import write_png  # TODO: add readme with visualization

yaml = ruamel.yaml.YAML(typ="safe")


@click.command()
@click.option(
    "--spec",
    type=click.File("r"),
    required=True,
    help="A workflow compilation YAML spec.",
)
@click.option(
    "--clobber/--no-clobber",
    is_flag=True,
    default=False,
    help="Whether or not to clobber an existing build directory.",
)
@click.option(
    "--lock/--no-lock",
    is_flag=True,
    default=True,
    help="Whether or not to generate a pixi lockfile for the package.",
)
def compile(
    spec: TextIOWrapper,
    clobber: bool,
    lock: bool,
):
    spec_text = spec.read()
    spec_sha256 = hashlib.sha256(spec_text.encode()).hexdigest()
    compilation_spec = Spec(**yaml.load(spec_text))
    dc = DagCompiler(spec=compilation_spec)
    dags = Dags(
        **{
            "jupytext.py": dc.generate_dag("jupytext"),
            "run_async_mock_io.py": dc.generate_dag("async", mock_io=True),
            "run_async.py": dc.generate_dag("async"),
            "run_sequential_mock_io.py": dc.generate_dag("sequential", mock_io=True),
            "run_sequential.py": dc.generate_dag("sequential"),
        }
    )
    wa = WorkflowArtifacts(
        spec_sha256=spec_sha256,
        spec_relpath=spec.name,
        package_name=dc.package_name,
        release_name=dc.release_name,
        pixi_toml=dc.get_pixi_toml(),
        pyproject_toml=dc.get_pyproject_toml(),
        package=PackageDirectory(
            dags=dags,
            params_jsonschema=dc.get_params_jsonschema(),
        ),
        tests=Tests(
            **{"conftest.py": dc.get_conftest()},
        ),
        dockerfile=dc.get_dockerfile(),
        # dag_png=write_png(dc.dag, "dag.png"),
        # readme=..., # TODO: readme with dag visualization
    )
    wa.dump(clobber=clobber)
    if lock:
        wa.lock()


@click.group()
def main():
    pass


main.add_command(compile)

if __name__ == "__main__":
    main()
