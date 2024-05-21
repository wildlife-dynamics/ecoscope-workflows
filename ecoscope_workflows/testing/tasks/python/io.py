from pathlib import Path

from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.tasks.python.io import SubjectGroupObservationsGDFSchema
from ecoscope_workflows.types import DataFrame

TEST_DATA_DIR = Path(__file__).parents[4] / "tests" / "data"


@distributed
def get_subjectgroup_observations() -> DataFrame[SubjectGroupObservationsGDFSchema]:
    import geopandas as gpd

    path = TEST_DATA_DIR / "subject-group.parquet"
    return gpd.read_parquet(path)
