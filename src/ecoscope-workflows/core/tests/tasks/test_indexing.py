import pandas as pd

from ecoscope_workflows.core.tasks.transformation import add_temporal_index


def test_add_temporal_index():
    df = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                ["2022-01-01", "2022-01-02", "2022-02-01", "2022-02-02"]
            ),
            "value": [1, 2, 3, 4],
        }
    )
    assert list(df.index.values) == [0, 1, 2, 3]

    with_month_index = add_temporal_index(
        df,
        index_name="month",
        time_col="timestamp",
        directive="%B",
    )
    assert list(with_month_index.index.values) == [
        (0, "January"),
        (1, "January"),
        (2, "February"),
        (3, "February"),
    ]
