from pathlib import Path

import pandas as pd

from ecoscope_workflows.serde import (
    HiveKey,
    load_gdf_from_hive_partitioned_parquet,
    persist_gdf_to_hive_partitioned_parquet,
)
from ecoscope_workflows.testing import generate_synthetic_gps_fixes_dataframe


def test_hive_partitioned_gdf_rountrip_group(tmp_path: Path):
    animal_names = ["Bo", "Jo", "Mo"]
    original = generate_synthetic_gps_fixes_dataframe(
        num_fixes=100,
        animal_names=animal_names,
    )
    path = persist_gdf_to_hive_partitioned_parquet(
        gdf=original,
        path=tmp_path / "test.parquet",
        partition_on=["animal_name"],
    )
    load_only_bo = load_gdf_from_hive_partitioned_parquet(
        path,
        filters=[HiveKey(column="animal_name", value="Bo")],
    )

    # cast to CategoricalDtype because that is how it's loaded back from
    # hive-partitioned parquet (even though it's just a string in the original)
    original["animal_name"] = pd.Categorical(
        original["animal_name"], categories=animal_names
    )

    # so in sum, this roundtrip is as if we had persisted a grouby object to parquet and
    # then could just load one group back at a time!
    groupby: dict[tuple[str], pd.DataFrame] = {
        k: v for k, v in original.groupby(["animal_name"])
    }
    pd.testing.assert_frame_equal(
        groupby[("Bo",)].sort_index(axis=1), load_only_bo.sort_index(axis=1)
    )
