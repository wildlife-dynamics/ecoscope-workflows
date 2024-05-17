import argparse
import yaml

from ecoscope_workflows.compiler import DagCompiler


def compile_command(args):
    compilation_spec = yaml.safe_load(args.spec)
    dc = DagCompiler(**compilation_spec)
    if args.template:
        dc.template = args.template
    dag_str = dc._generate_dag()
    if args.outpath:
        with open(args.outpath, "w") as f:
            f.write(dag_str)
    else:
        print(dag_str)


def tasks_command(args):
    # Implementation for tasks command
    print("Tasks command executed with args:", args)


def main():
    parser = argparse.ArgumentParser(prog='ecoscope-workflows')
    subparsers = parser.add_subparsers(title='subcommands', dest='command')
    
    # Subcommand 'compile'
    compile_parser = subparsers.add_parser('compile', help='Compile workflows')
    compile_parser.set_defaults(func=compile_command)
    compile_parser.add_argument(
        '--spec',
        dest='spec',
        required=True,
        type=argparse.FileType(mode='r'),
    )
    compile_parser.add_argument(
        '--template',
        dest='template',
        default='airflow-kubernetes.jinja2',
    )
    compile_parser.add_argument(
        '--outpath',
        dest='outpath',
    )

    # Subcommand 'tasks'
    tasks_parser = subparsers.add_parser('tasks', help='Manage tasks')
    tasks_parser.set_defaults(func=tasks_command)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
