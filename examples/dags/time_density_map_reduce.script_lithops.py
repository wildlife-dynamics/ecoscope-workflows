# import argparse
import functools
import os
from importlib import resources

import geopandas as gpd
# import yaml

from ecoscope_workflows.serde import (
    gdf_to_parquet_uri,
)
from ecoscope_workflows.tasks.setters import set_groupers, set_map_styles

# from ecoscope_workflows.tasks.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.parallelism import split_groups
from ecoscope_workflows.tasks.transformation import assign_from_column_attribute

if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # g = parser.add_argument_group("calculate_time_density")
    # g.add_argument(
    #     "--config-file",
    #     dest="config_file",
    #     required=True,
    #     type=argparse.FileType(mode="r"),
    # )
    # args = parser.parse_args()
    # params = yaml.safe_load(args.config_file)
    params = {  # represents user input via config file, etc.
        "set_groupers": dict(groupers={"groupers": ["month"]}),
        "set_map_styles": dict(map_styles={"map_styles": {}}),
        "assign_from_column_attribute": dict(
            column_name="month",
            dotted_attribute_name="extra__recorded_at.dt.month",
        ),
    }

    groupers = set_groupers.replace(validate=True)(**params["set_groupers"])
    map_styles = set_map_styles.replace(validate=True)(**params["set_map_styles"])

    # we're about to head into the distributed world, so we need to serialize
    # the geodataframe out to a cloud bucket or shared storage of some kind
    serialize_groups = functools.partial(
        gdf_to_parquet_uri,
        uri=os.environ["ECOSCOPE_WORKFLOWS_TMP"],  # cloud bucket, local disk, etc.
    )

    def get_subjectgroup_observations() -> gpd.GeoDataFrame:
        """Stand-in for actual `get_subjectgroup_observations` task, for demonstration purposes"""
        source_path = (
            resources.files("ecoscope_workflows.tasks.io")
            / "get-subjectgroup-observations.example-return.parquet"
        )
        return gpd.read_parquet(source_path)

    groups = (
        # get_subjectgroup_observations.replace(validate=True)(**params["get_subjectgroup_observations"])
        get_subjectgroup_observations()
        .pipe(
            assign_from_column_attribute.replace(validate=True),
            **params["assign_from_column_attribute"],
        )
        .pipe(
            split_groups.replace(validate=True, return_postvalidator=serialize_groups),
            **groupers,
        )
    )
    print(groups)
    # def gdf_pipe(gdf: gpd.GeoDataFrame):
    #     return (
    #         gdf.pipe(
    #             process_relocations.replace(
    #                 # the dataframe is given here as a list of URIs to parquet files,
    #                 # so we need to deserialize it back into a geodataframe
    #                 arg_prevalidators={"geodataframe": gpd_from_parquet_uri},
    #                 validate=True,
    #             ),
    #             **params["process_relocations"],
    #         )
    #         .pipe(
    #             relocations_to_trajectory.replace(validate=True),
    #             **params["relocations_to_trajectory"],
    #         )
    #         .pipe(
    #             calculate_time_density.replace(validate=True),
    #             **params["calculate_time_density"],
    #         )
    #         .pipe(
    #             draw_ecomap.replace(
    #                 return_postvalidator=functools.partial(
    #                     html_text_to_uri, uri=os.environ["ECOSCOPE_WORKFLOWS_TMP"]
    #                 ),
    #                 validate=True,
    #             )
    #             ** map_styles
    #         ),
    #     )

    # def map_function(gdf: gpd.GeoDataFrame):
    #     return map_to_widget(gdf_pipe(gdf))

    # # map reduce
    # # this can parallelize on local threads, gcp cloud run, or other cloud serverless
    # # compute backends, depending on the lithops configuration set at runtime.
    # map_reduce_return = map_reduce(
    #     groups=groups,
    #     map_function=map_function,
    #     reducer=gather_dashboard,
    #     reducer_kwargs=groupers,
    # )

    # print(map_reduce_return)
