import argparse
import functools
import os

import geopandas as gpd
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
from ecoscope_workflows.tasks.transformation import assign_from_column_attribute

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

    groupers = set_groupers.replace(validate=True)(**params["set_groupers"])
    map_styles = set_map_styles.replace(validate=True)(**params["set_map_styles"])

    # we're about to head into the distributed world, so we need to serialize
    # the geodataframe out to a cloud bucket or shared storage of some kind
    serialize_groups = functools.partial(
        gdf_to_parquet_uri,
        uri=os.environ["ECOSCOPE_WORKFLOWS_TMP"],  # cloud bucket, local disk, etc.
    )
    groups = (
        get_subjectgroup_observations.replace(validate=True)(
            **params["get_subjectgroup_observations"]
        )
        .pipe(
            assign_from_column_attribute.replace(validate=True),
            **params["assign_from_column_attribute"],
        )
        .pipe(
            split_groups.replace(validate=True, return_postvalidator=serialize_groups),
            **groupers,
        )
    )

    def gdf_pipe(gdf: gpd.GeoDataFrame):
        return (
            gdf.pipe(
                process_relocations.replace(
                    # the dataframe is given here as a list of URIs to parquet files,
                    # so we need to deserialize it back into a geodataframe
                    arg_prevalidators={"geodataframe": gpd_from_parquet_uri},
                    validate=True,
                ),
                **params["process_relocations"],
            )
            .pipe(
                relocations_to_trajectory.replace(validate=True),
                **params["relocations_to_trajectory"],
            )
            .pipe(
                calculate_time_density.replace(validate=True),
                **params["calculate_time_density"],
            )
            .pipe(
                draw_ecomap.replace(
                    return_postvalidator=functools.partial(
                        html_text_to_uri, uri=os.environ["ECOSCOPE_WORKFLOWS_TMP"]
                    ),
                    validate=True,
                )
                ** map_styles
            ),
        )

    def map_function(gdf: gpd.GeoDataFrame):
        return map_to_widget(gdf_pipe(gdf))

    # map reduce
    # this can parallelize on local threads, gcp cloud run, or other cloud serverless
    # compute backends, depending on the lithops configuration set at runtime.
    map_reduce_return = map_reduce(
        groups=groups,
        map_function=map_function,
        reducer=gather_dashboard,
        reducer_kwargs=groupers,
    )

    print(map_reduce_return)
