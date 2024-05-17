import argparse
import yaml
from ecoscope_workflows.tasks.python.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.python.preprocessing import process_relocations

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    g = parser.add_argument_group('calculate_time_density')
    g.add_argument(
        '--config-file',
        dest='config_file',
        required=True,
        type=argparse.FileType(mode='r'),
    )
    args = parser.parse_args()
    # TODO: omit fields which are listed in arg_dependencies at the TaskInstance level
    params = yaml.safe_load(args.config_file)
    # FIXME: first pass assumes tasks are already in topological order
    
    get_subjectgroup_observations_return = get_subjectgroup_observations.replace(validate=True)(params["get_subjectgroup_observations"])
    
    process_relocations_return = process_relocations.replace(validate=True)(
        observations=get_subjectgroup_observations_return,
        **params["process_relocations"])
