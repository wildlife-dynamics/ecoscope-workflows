import pandas as pd
import pandera as pa
import pandera.typing as pa_typing
import pytest
from pydantic import BaseModel, ValidationError

from ecoscope_workflows_core.annotations import (
    DataFrame,
    JsonSerializableDataFrameModel,
)


def test_dataframe_type():
    df = pd.DataFrame(data={"col1": [1, 2]})

    class ValidSchema(JsonSerializableDataFrameModel):
        col1: pa_typing.Series[int] = pa.Field(unique=True)

    class ValidModel(BaseModel):
        df: DataFrame[ValidSchema]

    ValidModel(df=df)

    class InvalidSchema(JsonSerializableDataFrameModel):
        # Invalid because col1 elements are ints, not strings
        col1: pa_typing.Series[str] = pa.Field(unique=True)

    class InvalidModel(BaseModel):
        df: DataFrame[InvalidSchema]

    with pytest.raises(ValidationError):
        InvalidModel(df=df)
