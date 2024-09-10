from typing import Annotated, Literal, TYPE_CHECKING, cast

from pydantic import Field

from ecoscope_workflows.annotations import AnyDataFrame
from ecoscope_workflows.decorators import task


# TODO: Leverage this information to generate more readable documentation
# for the `directive` parameter of `add_temporal_index` task. For now, this
# is not used anywhere, but leaving it here for future reference.
strftime_directives = {
    "%a": "Locale's abbreviated weekday name.",
    "%A": "Locale's full weekday name.",
    "%b": "Locale's abbreviated month name.",
    "%B": "Locale's full month name.",
    "%c": "Locale's appropriate date and time representation.",
    "%d": "Day of the month as a decimal number [01,31].",
    "%f": "Microseconds as a decimal number [000000,999999].",
    "%H": "Hour (24-hour clock) as a decimal number [00,23].",
    "%I": "Hour (12-hour clock) as a decimal number [01,12].",
    "%j": "Day of the year as a decimal number [001,366].",
    "%m": "Month as a decimal number [01,12].",
    "%M": "Minute as a decimal number [00,59].",
    "%p": "Locale's equivalent of either AM or PM.",
    "%S": "Second as a decimal number [00,61].",
    "%U": "Week number of the year (Sunday as the first day of the week) as a decimal number [00,53].",
    "%w": "Weekday as a decimal number [0(Sunday),6].",
    "%W": "Week number of the year (Monday as the first day of the week) as a decimal number [00,53].",
    "%x": "Locale's appropriate date representation.",
    "%X": "Locale's appropriate time representation.",
    "%y": "Year without century as a decimal number [00,99].",
    "%Y": "Year with century as a decimal number.",
    "%z": "Time zone offset indicating a positive or negative time difference from UTC/GMT of the form +HHMM or -HHMM.",
    "%%": "A literal '%' character.",
}

Directives = Literal[
    "%a",
    "%A",
    "%b",
    "%B",
    "%c",
    "%d",
    "%f",
    "%H",
    "%I",
    "%j",
    "%m",
    "%M",
    "%p",
    "%S",
    "%U",
    "%w",
    "%W",
    "%x",
    "%X",
    "%y",
    "%Y",
    "%z",
    "%%",
]


@task
def add_temporal_index(
    df: Annotated[
        AnyDataFrame, Field(description="The dataframe to add the temporal index to.")
    ],
    index_name: Annotated[
        str, Field(description="A name for the new index which will be added.")
    ],
    time_col: Annotated[
        str, Field(description="Name of existing column containing time data.")
    ],
    directive: Annotated[
        Directives, Field(description="A directive for formatting the time data.")
    ],
    cast_to_datetime: Annotated[
        bool,
        Field(
            description="Whether to attempt casting `time_col` to datetime.",
        ),
    ] = True,
    format: Annotated[
        str,
        Field(
            description="""\
            If `cast_to_datetime=True`, the format to pass to `pd.to_datetime`
            when attempting to cast `time_col` to datetime. Defaults to "mixed".
            """,
        ),
    ] = "mixed",
) -> AnyDataFrame:
    import pandas as pd

    if TYPE_CHECKING:
        cast(pd.DataFrame, df)

    if cast_to_datetime:
        df[time_col] = pd.to_datetime(df[time_col], format=format)

    df[index_name] = df[time_col].dt.strftime(directive)
    return df.set_index(index_name, append=True)
