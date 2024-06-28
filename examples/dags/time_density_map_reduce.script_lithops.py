import os
import time
from pathlib import Path


# from ecoscope_workflows.tasks.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.setters import set_groupers, set_map_styles
from ecoscope_workflows.tasks.analysis import calculate_time_density

from ecoscope_workflows.tasks.parallelism import map_reduce
from ecoscope_workflows.tasks.preprocessing import (
    process_relocations,
    relocations_to_trajectory,
)
from ecoscope_workflows.tasks.results import (
    draw_ecomap,
    gather_dashboard,
    gather_widget,
)
from ecoscope_workflows.tasks.transformation import assign_temporal_column
from ecoscope_workflows.serde import (
    groupbykeys_to_hivekeys,
    load_gdf_from_hive_partitioned_parquet,
    persist_html_text,
    persist_gdf_to_hive_partitioned_parquet,
    storage_object_key_from_composite_hivekey,
)
from ecoscope_workflows.testing import generate_synthetic_gps_fixes_dataframe

# represents user input via config file, web frontend form, etc.
# these params would not be hardcoded in a real-world application
params = {
    "set_groupers": dict(
        groupers={"groupers": ["animal_name", "month"]},
    ),
    "set_map_styles": dict(
        map_styles={"map_styles": {}},
    ),
    "assign_temporal_column": dict(
        col_name="month",
        time_col="fixtime",
        directive="%B",  # month name
    ),
    "process_relocations": dict(
        filter_point_coords=[[180, 90], [0, 0]],
        relocs_columns=["groupby_col", "fixtime", "junk_status", "geometry"],
    ),
    "relocations_to_trajectory": dict(
        min_length_meters=0.001,
        max_length_meters=10000,
        max_time_secs=3600,
        min_time_secs=1,
        max_speed_kmhr=120,
        min_speed_kmhr=0.0,
    ),
    "calculate_time_density": dict(
        pixel_size=250.0,
        crs="ESRI:102022",
        nodata_value="nan",
        band_count=1,
        max_speed_factor=1.05,
        expansion_factor=1.3,
        percentiles=[50.0, 60.0, 70.0, 80.0, 90.0, 95.0],
    ),
    "draw_ecomap": dict(
        static=False,
        height=1000,
        width=1500,
        search_control=True,
        title="Great Map",
        title_kws={},
        tile_layers=[],
        north_arrow_kws={},
        add_gdf_kws={},
    ),
    "gather_widget": dict(
        widget_type="ecomap",
        title="Time Density Ecomap",
    ),
}
# override get_subjectgroup_observations with synthetic data generator
# for demonstration purposes; remove this line to use real data
get_subjectgroup_observations = generate_synthetic_gps_fixes_dataframe

if __name__ == "__main__":
    ECOSCOPE_WORKFLOWS_TMP = Path(os.environ.get("ECOSCOPE_WORKFLOWS_TMP", "."))
    JOB_ID = os.environ.get("JOB_ID", f"job-{int(time.monotonic())}")
    TMP_PARQUET = (ECOSCOPE_WORKFLOWS_TMP / JOB_ID / "tmp.parquet").absolute().as_uri()
    RESULTS_DIR = ECOSCOPE_WORKFLOWS_TMP / JOB_ID / "results"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

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
        {"element": (nested_hk, str(df_url))}
        for nested_hk in groupbykeys_to_hivekeys(df, **groupers)
        # {"element": ((('animal_name', '=', 'Bo'), ('month', '=', 'January')), "gcs://bucket/tmp/job-3456788/tmp.parquet")}
    ]

    def map_function(element: tuple[tuple, str]) -> tuple[tuple, str]:
        composite_hivekey, df_url = element

        df = load_gdf_from_hive_partitioned_parquet(
            path=df_url,
            filters=composite_hivekey,
            crs="EPSG:4326",
        )
        reloc = process_relocations.replace(validate=True)(
            df, **params["process_relocations"]
        )
        traj = relocations_to_trajectory.replace(validate=True)(
            reloc, **params["relocations_to_trajectory"]
        )
        td = calculate_time_density.replace(validate=True)(
            traj, **params["calculate_time_density"]
        )
        html_text = draw_ecomap.replace(validate=True)(td, **params["draw_ecomap"])
        return composite_hivekey, persist_html_text(
            html_text,
            path=RESULTS_DIR
            / storage_object_key_from_composite_hivekey(composite_hivekey),
        )

    def reduce_function(results: list[tuple[tuple, str]]) -> list[str]:
        return gather_widget.replace(validate=True)(results, **params["gather_widget"])

    # this can parallelize on local threads, gcp cloud run, or other cloud serverless
    # compute backends, depending on the lithops configuration set at runtime.
    time_density_ecomap_widget = map_reduce(
        groups=parallel_collection,
        map_function=map_function,
        reduce_function=reduce_function,
    )

    dashboard = gather_dashboard(widgets=[time_density_ecomap_widget], **groupers)
    print(dashboard)
