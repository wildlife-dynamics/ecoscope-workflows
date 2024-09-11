import numpy as np
import pandas as pd
import pytest

from ecoscope_workflows.tasks.transformation._classification import (
    apply_classification,
    apply_color_map,
    SharedArgs,
    MaxBreaksArgs,
    StdMeanArgs,
    NaturalBreaksArgs,
    CustomLabels,
    DefaultLabels,
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
    "scheme, classification_args, label_args",
    [
        (
            "equal_interval",
            SharedArgs(k=3),
            DefaultLabels(label_ranges=True, label_decimals=0),
        ),
        (
            "max_breaks",
            MaxBreaksArgs(k=4, min_diff=20),
            DefaultLabels(label_prefix="_", label_suffix="_"),
        ),
        (
            "natural_breaks",
            NaturalBreaksArgs(k=4, initial=3),
            CustomLabels(labels=["One", "Two", "Three", "Four"]),
        ),
        ("std_mean", StdMeanArgs(multiples=[-1, 1], anchor=False), DefaultLabels()),
    ],
)
def test_apply_classification(test_df, scheme, classification_args, label_args):
    result = apply_classification(
        df=test_df,
        input_column_name="column_name",
        scheme=scheme,
        output_column_name="classified",
        label_options=label_args,
        classification_options=classification_args,
    )

    assert "classified" in result.columns
