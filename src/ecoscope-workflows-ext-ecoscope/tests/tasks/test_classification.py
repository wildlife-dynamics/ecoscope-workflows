import numpy as np
import pandas as pd
import pytest
from ecoscope_workflows_ext_ecoscope.tasks.transformation._classification import (
    MaxBreaksArgs,
    NaturalBreaksArgs,
    SharedArgs,
    StdMeanArgs,
    apply_classification,
    apply_color_map,
)


@pytest.fixture
def test_df():
    return pd.DataFrame({"column_name": [5, 3, 1, 6, 5, 9]})


def test_color_map():
    df = pd.DataFrame({"column_name": ["A", "B", "A", "C", "B", "C"]})
    result = apply_color_map(df, "column_name", ["#FF0000", "#00FF00", "#0000FF"])

    assert "column_name_colormap" in result.columns

    color_mapping = {
        "A": (255, 0, 0, 255),
        "B": (0, 255, 0, 255),
        "C": (0, 0, 255, 255),
    }
    for _, row in result.iterrows():
        np.testing.assert_array_equal(
            row["column_name_colormap"],
            color_mapping[row["column_name"]],
        )


@pytest.mark.parametrize(
    "scheme, args",
    [
        ("equal_interval", SharedArgs(scheme="equal_interval", k=3)),
        ("max_breaks", MaxBreaksArgs(scheme="max_breaks", k=4, min_diff=20)),
        ("natural_breaks", NaturalBreaksArgs(scheme="natural_breaks", k=4, initial=3)),
        ("std_mean", StdMeanArgs(scheme="std_mean", multiples=[-1, 1], anchor=False)),
    ],
)
def test_apply_classification_equal_interval(test_df, scheme, args):
    result = apply_classification(
        df=test_df,
        input_column_name="column_name",
        output_column_name="classified",
        classification_options=args,
    )

    assert "classified" in result.columns
