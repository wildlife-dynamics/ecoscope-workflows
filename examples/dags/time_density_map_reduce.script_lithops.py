import os
from pathlib import Path

import geopandas as gpd

# from ecoscope_workflows.tasks.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.setters import set_groupers, set_map_styles
from ecoscope_workflows.tasks.analysis import calculate_time_density
from ecoscope_workflows.tasks.preprocessing import (
    process_relocations,
    relocations_to_trajectory,
)
from ecoscope_workflows.tasks.transformation import assign_temporal_column
from ecoscope_workflows.serde import (
    groupbykeys_to_hivekeys,
    persist_gdf_to_hive_partitioned_parquet,
)
from ecoscope_workflows.testing import generate_synthetic_gps_fixes_dataframe

params = {  # represents user input via config file, http, etc.
    "set_groupers": dict(groupers={"groupers": ["animal_name", "month"]}),
    "set_map_styles": dict(map_styles={"map_styles": {}}),
    "assign_temporal_column": dict(
        col_name="month",
        time_col="fixtime",
        directive="%B",  # month name
    ),
}
# override get_subjectgroup_observations with synthetic data generator
# for demonstration purposes; remove this line to use real data
get_subjectgroup_observations = generate_synthetic_gps_fixes_dataframe

if __name__ == "__main__":
    ECOSCOPE_WORKFLOWS_TMP = Path(os.environ.get("ECOSCOPE_WORKFLOWS_TMP", "."))
    JOB_ID = os.environ.get("JOB_ID", "test-job-id")
    TMP_PARQUET = (ECOSCOPE_WORKFLOWS_TMP / JOB_ID / "tmp.parquet").absolute().as_uri()

    groupers = set_groupers.replace(validate=True)(**params["set_groupers"])
    map_styles = set_map_styles.replace(validate=True)(**params["set_map_styles"])

    df = get_subjectgroup_observations().pipe(  # no .replace() or args bc using with synthetic data
        assign_temporal_column.replace(validate=True),
        **params["assign_temporal_column"],
    )

    df_url = df.pipe(
        persist_gdf_to_hive_partitioned_parquet,
        partition_on=groupers["groupers"],
        path=TMP_PARQUET,
    )

    parallel_collection = [
        (nested_hk, str(df_url))
        for nested_hk in groupbykeys_to_hivekeys(df, **groupers)
        # e.g., (('animal_name', '=', 'Bo'), ('month', '=', 'January')), "gcs://bucket/tmp.parquet"
    ]
    print(parallel_collection)

    def gdf_pipe(gdf: gpd.GeoDataFrame):
        return (
            gdf.pipe(
                process_relocations.replace(
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
