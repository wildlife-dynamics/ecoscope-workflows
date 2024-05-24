import argparse
import json

import yaml

from ecoscope_workflows.compiler import DagCompiler
from ecoscope_workflows.registry import known_tasks


def compile_command(args):
    compilation_spec = yaml.safe_load(args.spec)
    dc = DagCompiler.from_spec(spec=compilation_spec)
    if args.template:
        dc.template = args.template
    if args.testing:
        dc.testing = True
    if args.mock_tasks:
        dc.mock_tasks = args.mock_tasks
    dag_str = dc._generate_dag()
    if args.outpath:
        with open(args.outpath, "w") as f:
            f.write(dag_str)
    else:
        print(dag_str)


def tasks_command(args):
    print()
    for t, kt in known_tasks.items():
        print(f"{t}:")
        for field, val in kt.model_dump().items():
            print(f"    {field}: {val}")
        print("\n")


def get_params_command(args):
    compilation_spec = yaml.safe_load(args.spec)
    dc = DagCompiler.from_spec(spec=compilation_spec)
    if args.format == "json":
        params = dc.dag_params_schema()
    elif args.format == "yaml":
        params = dc.dag_params_yaml()
    if args.outpath:
        with open(args.outpath, "w") as f:
            if args.format == "json":
                json.dump(params, f, indent=4)
            elif args.format == "yaml":
                f.write(params)
    else:
        print(params)


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
        "--template",
        dest="template",
        default="airflow-kubernetes.jinja2",
    )
    compile_parser.add_argument(
        "--outpath",
        dest="outpath",
    )
    compile_parser.add_argument(
        "--testing",
        action=argparse.BooleanOptionalAction,
    )
    compile_parser.add_argument(
        "--mock-tasks",
        dest="mock_tasks",
        nargs="+",
    )

    # Subcommand 'tasks'
    tasks_parser = subparsers.add_parser("tasks", help="Manage tasks")
    tasks_parser.set_defaults(func=tasks_command)

    # Subcommand 'get-params'
    get_params_parser = subparsers.add_parser("get-params", help="Get params")
    get_params_parser.set_defaults(func=get_params_command)
    # FIXME: duplicative with `compile`
    get_params_parser.add_argument(
        "--spec",
        dest="spec",
        required=True,
        type=argparse.FileType(mode="r"),
    )
    get_params_parser.add_argument(
        "--outpath",
        dest="outpath",
    )
    get_params_parser.add_argument(
        "--format",
        dest="format",
        default="json",
    )

    # Parse args
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
