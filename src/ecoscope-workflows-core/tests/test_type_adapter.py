from typing import Annotated

import numpy as np
import pandera as pa
import pytest
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from ecoscope_workflows_core.decorators import task
from ecoscope_workflows_core.jsonschema import SurfacesDescriptionSchema
from ecoscope_workflows_core.annotations import (
    DataFrame,
    JsonSerializableDataFrameModel,
)


def test_jsonschema_from_signature_basic():
    class FuncSignature(BaseModel):
        model_config = ConfigDict(extra="forbid")

        foo: int
        bar: str

    def func(foo: int, bar: str): ...

    from_func = TypeAdapter(func).json_schema()
    from_model = FuncSignature.model_json_schema()
    del from_model["title"]  # TypeAdapter(func).json_schema() has no "title"
    assert from_func == from_model


def test_jsonschema_from_signature_basic_task():
    class FuncSignature(BaseModel):
        model_config = ConfigDict(extra="forbid")

        foo: int
        bar: str

    @task
    def func(foo: int, bar: str): ...

    from_func = TypeAdapter(func.func).json_schema()
    from_model = FuncSignature.model_json_schema()
    del from_model["title"]  # TypeAdapter(func).json_schema() has no "title"
    assert from_func == from_model


def test_DataFrameModel_generate_schema():
    class Schema(JsonSerializableDataFrameModel):
        col1: pa.typing.Series[int] = pa.Field(unique=True)

    schema = TypeAdapter(Schema).json_schema()
    assert schema == Schema.to_json_schema()


def test_DataFrame_generate_schema():
    class Schema(JsonSerializableDataFrameModel):
        col1: pa.typing.Series[int] = pa.Field(unique=True)

    Foo = DataFrame[Schema]
    schema = TypeAdapter(Foo).json_schema()
    assert schema == {"type": "ecoscope_workflows.annotations.DataFrame"}


@pytest.mark.skip(
    reason="Passes locally but hangs in CI; possibly due to numpy version?"
)
def test_jsonschema_from_signature_nontrivial():
    config_dict = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    class Schema(JsonSerializableDataFrameModel):
        col1: pa.typing.Series[int] = pa.Field(unique=True)

    class TimeDensityConfig(BaseModel):
        model_config = config_dict

        input_df: DataFrame[Schema]
        pixel_size: Annotated[
            float,
            Field(default=250.0, description="Pixel size for raster profile."),
        ]
        crs: Annotated[str, Field(default="ESRI:102022")]
        nodata_value: Annotated[float, Field(default=float("nan"), allow_inf_nan=True)]
        band_count: Annotated[int, Field(default=1)]
        max_speed_factor: Annotated[float, Field(default=1.05)]
        expansion_factor: Annotated[float, Field(default=1.3)]
        percentiles: Annotated[
            list[float], Field(default=[50.0, 60.0, 70.0, 80.0, 90.0, 95.0])
        ]

    def calculate_time_density(
        input_df: DataFrame[Schema],
        pixel_size: Annotated[
            float,
            Field(default=250.0, description="Pixel size for raster profile."),
        ],
        crs: Annotated[str, Field(default="ESRI:102022")],
        nodata_value: Annotated[float, Field(default=float("nan"), allow_inf_nan=True)],
        band_count: Annotated[int, Field(default=1)],
        max_speed_factor: Annotated[float, Field(default=1.05)],
        expansion_factor: Annotated[float, Field(default=1.3)],
        percentiles: Annotated[
            list[float], Field(default=[50.0, 60.0, 70.0, 80.0, 90.0, 95.0])
        ],
    ): ...

    schema_kws = dict(schema_generator=SurfacesDescriptionSchema)
    from_func = TypeAdapter(
        calculate_time_density,
        config=config_dict,
    ).json_schema(**schema_kws)
    from_model = TimeDensityConfig.model_json_schema(**schema_kws)
    del from_model["title"]  # TypeAdapter(func).json_schema() has no "title"
    # `nodata_value` defaults to `nan`; numpy evals `nan == nan` as true
    np.testing.assert_equal(from_func, from_model)
