import argparse

import ruamel.yaml

from ecoscope_workflows_core.artifacts import (
    Dags,
    PackageDirectory,
    Tests,
    WorkflowArtifacts,
)
from ecoscope_workflows_core.compiler import DagCompiler, Spec

yaml = ruamel.yaml.YAML(typ="safe")


def compile_command(args):
    compilation_spec = Spec(**yaml.load(args.spec))
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
        package_name=dc.package_name,
        release_name=dc.release_name,
        pixi_toml=dc.get_pixi_toml(),
        pyproject_toml=dc.get_pyproject_toml(),
        package=PackageDirectory(
            dags=dags,
            params_jsonschema=dc.get_params_jsonschema(),
        ),
        tests=Tests(
            **{"test_dags.py": dc.get_test_dags()},
        ),
    )
    wa.dump(clobber=args.clobber)
    if args.lock:
        wa.lock()


def visualize(args):
    from ecoscope_workflows_core.visualize import write_png

    compilation_spec = Spec(**yaml.load(args.spec))
    outpath = args.outpath
    write_png(compilation_spec, outpath)


def main():
    parser = argparse.ArgumentParser(prog="ecoscope-workflows")
    subparsers = parser.add_subparsers(title="subcommands", dest="command")

    # Subcommand 'compile'
    compile_parser = subparsers.add_parser("compile", help="Compile workflows")
    compile_parser.set_defaults(func=compile_command)
    compile_parser.add_argument(
        "--spec",
        dest="spec",
        required=True,
        type=argparse.FileType(mode="r"),
    )
    compile_parser.add_argument(
        "--clobber",
        dest="clobber",
        default=False,
        action="store_true",
    )
    compile_parser.add_argument(
        "--lock",
        dest="lock",
        default=True,
        action="store_true",
    )

    # Subcommand 'visualize'
    visualize_parser = subparsers.add_parser("visualize", help="Visualize workflows")
    visualize_parser.set_defaults(func=visualize)
    visualize_parser.add_argument(
        "--spec",
        dest="spec",
        required=True,
        type=argparse.FileType(mode="r"),
    )
    visualize_parser.add_argument(
        "--outpath",
        dest="outpath",
    )


if __name__ == "__main__":
    main()
