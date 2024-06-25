import matplotlib
import numpy as np
import pandas as pd

from ecoscope_workflows.tasks.transformation._classification import color_map


def test_color_map():
    df = pd.DataFrame({"column_name": ["A", "B", "A", "C", "B", "C"]})
    result = color_map(df, "column_name", "viridis")

    assert "label" in result.columns

    color_mapping = {"A": 0, "B": 1, "C": 2}
    for _, row in result.iterrows():
        np.testing.assert_array_equal(
            row["label"],
            matplotlib.colormaps["viridis"](color_mapping[row["column_name"]]),
        )
