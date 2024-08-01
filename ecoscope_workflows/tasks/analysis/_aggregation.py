from typing import Annotated, Literal

import pandas as pd
from pydantic import Field

from ecoscope_workflows.annotations import DataFrame, JsonSerializableDataFrameModel
from ecoscope_workflows.decorators import distributed


@distributed
def aggregate(
    df: DataFrame[JsonSerializableDataFrameModel],
    column_name: Annotated[str, Field(description="Column to aggregate")],
    func_name: Annotated[
        Literal["count", "mean", "sum"], Field(description="The method of aggregation")
    ],
) -> DataFrame[JsonSerializableDataFrameModel]:
    match func_name.upper():
        case "COUNT":
            return pd.Series({f"{column_name}_count": len(df)})
        case "MEAN":
            return pd.Series({f"{column_name}_mean": df[column_name].mean()})
        case "SUM":
            return pd.Series({f"{column_name}_sum": df[column_name].sum()})
        case _:
            raise ValueError(f"Unknown aggregation function: {func_name}")
