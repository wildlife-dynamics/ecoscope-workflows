import pandas as pd

from ecoscope_workflows.tasks.transformation import assign_from_column_attribute


def test_assign_from_column_attribute():
    df = pd.DataFrame(
        {
            "recorded_at": [
                pd.Timestamp("2021-01"),
                pd.Timestamp("2021-01"),
                pd.Timestamp("2021-02"),
                pd.Timestamp("2021-02"),
                pd.Timestamp("2021-03"),
            ],
            "value": [5, 6, 7, 8, 9],
        }
    )
    df_new = assign_from_column_attribute(
        df, column_name="month", dotted_attribute_name="recorded_at.dt.month"
    )
    assert "month" in df_new.columns
    assert df_new["month"].tolist() == [1, 1, 2, 2, 3]
