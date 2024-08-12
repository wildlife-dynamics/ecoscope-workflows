import pandas as pd
import pandera as pa
import pytest
from pydantic import BaseModel, ValidationError

from ecoscope_workflows.annotations import (
    DataFrame,
    EarthRangerClient,
    JsonSerializableDataFrameModel,
    is_client,
)


def test_dataframe_type():
    df = pd.DataFrame(data={"col1": [1, 2]})

    class ValidSchema(JsonSerializableDataFrameModel):
        col1: pa.typing.Series[int] = pa.Field(unique=True)

    class ValidModel(BaseModel):
        df: DataFrame[ValidSchema]

    ValidModel(df=df)

    class InvalidSchema(JsonSerializableDataFrameModel):
        # Invalid because col1 elements are ints, not strings
        col1: pa.typing.Series[str] = pa.Field(unique=True)

    class InvalidModel(BaseModel):
        df: DataFrame[InvalidSchema]

    with pytest.raises(ValidationError):
        InvalidModel(df=df)


def test_is_client():
    assert is_client(EarthRangerClient)
    assert not is_client(DataFrame)
