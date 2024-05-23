import argparse
import yaml

from ecoscope_workflows.tasks.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.preprocessing import process_relocations
from ecoscope_workflows.tasks.preprocessing import relocations_to_trajectory
from ecoscope_workflows.tasks.analysis import calculate_time_density

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    g = parser.add_argument_group("calculate_time_density")
    g.add_argument(
        "--config-file",
        dest="config_file",
        required=True,
        type=argparse.FileType(mode="r"),
    )
    args = parser.parse_args()
    params = yaml.safe_load(args.config_file)
    # FIXME: first pass assumes tasks are already in topological order

    get_subjectgroup_observations_return = get_subjectgroup_observations.replace(
        validate=True
    )(
        **params["get_subjectgroup_observations"],
    )

    process_relocations_return = process_relocations.replace(validate=True)(
        observations=get_subjectgroup_observations_return,
        **params["process_relocations"],
    )

    relocations_to_trajectory_return = relocations_to_trajectory.replace(validate=True)(
        relocations=process_relocations_return,
        **params["relocations_to_trajectory"],
    )

    calculate_time_density_return = calculate_time_density.replace(validate=True)(
        trajectory_gdf=relocations_to_trajectory_return,
        **params["calculate_time_density"],
    )
