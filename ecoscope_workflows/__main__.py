import argparse
import yaml

from ecoscope_workflows.compiler import DagCompiler

def parse_args():
    parser = argparse.ArgumentParser()
    g = parser.add_argument_group('Ecoscope Workflows')
    g.add_argument(
        '--compilation-spec-file',
        dest='compilation_spec_file',
        required=True,
        type=argparse.FileType(mode='r'),
    )
    return parser.parse_args()


def main():
    args = parse_args()
    compilation_spec = yaml.safe_load(args.compilation_spec_file)
    dc = DagCompiler(**compilation_spec)
    dag_str = dc._generate_dag()
    print(dag_str)

if __name__ == "__main__":
    main()
