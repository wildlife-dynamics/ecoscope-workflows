import argparse
import functools
import os

import yaml

from ecoscope_workflows.serde import (
    gpd_from_parquet_uri,
    gdf_to_parquet_uri,
    html_text_to_uri,
)
from ecoscope_workflows.tasks.setters import set_groupers, set_map_styles
from ecoscope_workflows.tasks.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.preprocessing import process_relocations
from ecoscope_workflows.tasks.preprocessing import relocations_to_trajectory
from ecoscope_workflows.tasks.analysis import calculate_time_density
from ecoscope_workflows.tasks.parallelism import map_reduce, split_groups
from ecoscope_workflows.tasks.results import (
    draw_ecomap,
    map_to_widget,
    gather_dashboard,
)

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

    set_groupers_return = set_groupers.replace(validate=True)(
        **params["set_groupers"],
    )

    set_map_styles_return = set_map_styles.replace(validate=True)(
        **params["set_map_styles"],
    )

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

    # map reduce
    split_groups_return = split_groups.replace(
        # we're about to head into the distributed world, so we need to serialize
        # the geodataframe out to a cloud bucket or shared storage of some kind
        return_postvalidator=functools.partial(
            gdf_to_parquet_uri,
            uri=os.environ["ECOSCOPE_WORKFLOWS_TMP"],  # cloud bucket, local disk, etc.
        ),
        validate=True,
    )(
        groupers=set_groupers_return,
        dataframe=calculate_time_density_return,
    )
    # this can parallelize on local threads, gcp cloud run, or other cloud serverless
    # compute backends, depending on the lithops configuration set at runtime.
    map_reduce_return = map_reduce(
        groups=split_groups_return,
        mappers=[
            (
                draw_ecomap.replace(
                    # the dataframe is given here as a list of URIs to parquet files,
                    # so we need to deserialize it back into a geodataframe
                    arg_prevalidators={"geodataframe": gpd_from_parquet_uri},
                    return_postvalidator=functools.partial(
                        html_text_to_uri,
                        uri=os.environ["ECOSCOPE_WORKFLOWS_TMP"],
                    ),
                    validate=True,
                ),
                set_map_styles_return,
            ),
            (
                map_to_widget.replace(validate=True),
                {},
            ),
        ],
        reducer=gather_dashboard,
        reducer_kwargs=set_groupers_return,
    )

    print(map_reduce_return)
