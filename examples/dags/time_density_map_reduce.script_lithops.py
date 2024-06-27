import os
from collections import namedtuple
from pathlib import Path

import dask_geopandas as daskgpd
import geopandas as gpd

from ecoscope_workflows.tasks.setters import set_groupers, set_map_styles
from ecoscope_workflows.tasks.analysis import calculate_time_density
# from ecoscope_workflows.tasks.parallelism import split_groups
from ecoscope_workflows.tasks.preprocessing import process_relocations, relocations_to_trajectory
from ecoscope_workflows.tasks.transformation import assign_temporal_column
from ecoscope_workflows.testing import generate_synthetic_gps_fixes_dataframe

params = {  # represents user input via config file, http, etc.
    "set_groupers": dict(groupers={"groupers": ["month"]}),
    "set_map_styles": dict(map_styles={"map_styles": {}}),
    "assign_temporal_column": dict(
        col_name="month",
        time_col="fixtime",
        directive="%B",  # month name
    ),
}

if __name__ == "__main__":
    TMP = Path(os.environ.get("ECOSCOPE_WORKFLOWS_TMP", "."))

    groupers = set_groupers
    map_styles = set_map_styles.replace(validate=True)(**params["set_map_styles"])

    df = (
        generate_synthetic_gps_fixes_dataframe(num_fixes=1000)  # stand-in for real data
        .pipe(assign_temporal_column.replace(validate=True), **params["assign_temporal_column"])
    )
    # TODO: encapulate writing to parquet in a task
    ddf: daskgpd.GeoDataFrame = daskgpd.from_geopandas(df, npartitions=1)
    ddf.to_parquet(TMP / "synth.parquet", partition_on=["month", "animal_name"])


    def _groupkey_to_hivekey(groupkey: tuple[str], groupers) -> HiveKey:
        return tuple(
            [
                HiveKey(groupers[i], "=", groupkey[i])
            ])

    def get_hive_keys(df: gpd.GeoDataFrame, groupers: list[str]) -> tuple[HiveKey, ...]:
        return [
            HiveKey(column=group, "=", value=key)
            df.groupby(groupers=groupers)
        ]

    def gdf_pipe(gdf: gpd.GeoDataFrame):
        return (
            gdf
            .pipe(
                process_relocations.replace(
                validate=True,
            ),
            **params["process_relocations"],
            ).pipe(
                relocations_to_trajectory.replace(validate=True), **params["relocations_to_trajectory"])
            .pipe(calculate_time_density.replace(validate=True), **params["calculate_time_density"])
            # .pipe(
            #     draw_ecomap.replace(
            #         validate=True,
            #         # return_postvalidator=
            #     )
            #     ** map_styles
            # ),
            )

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
