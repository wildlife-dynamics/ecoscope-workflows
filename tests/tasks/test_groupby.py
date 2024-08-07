import numpy as np
import pandas as pd

import pytest

from ecoscope_workflows.indexes import CompositeFilter, IndexName, IndexValue
from ecoscope_workflows.tasks.groupby import set_groupers, split_groups
from ecoscope_workflows.tasks.groupby._groupby import (
    Grouper,
    _groupkey_to_composite_filter,
)


def test_set_groupers():
    input_groupers = [Grouper(index_name="class"), Grouper(index_name="order")]
    output_groupers = set_groupers(input_groupers)
    assert input_groupers == output_groupers


@pytest.mark.parametrize(
    "groupers, index_values, expected",
    [
        (
            ["class", "order"],
            ("bird", "Falconiformes"),
            (("class", "=", "bird"), ("order", "=", "Falconiformes")),
        ),
        (
            ["month", "year"],
            ("jan", "2022"),
            (("month", "=", "jan"), ("year", "=", "2022")),
        ),
    ],
)
def test__groupkey_to_composite_filter(
    groupers: list[IndexName],
    index_values: tuple[IndexValue, ...],
    expected: CompositeFilter,
):
    composite_filter = _groupkey_to_composite_filter(groupers, index_values)
    assert composite_filter == expected


def test_split_groups():
    df = pd.DataFrame(
        [
            ("bird", "Falconiformes", 389.0),
            ("bird", "Psittaciformes", 24.0),
            ("mammal", "Carnivora", 80.2),
            ("mammal", "Primates", np.nan),
            ("mammal", "Carnivora", 58),
        ],
        index=["falcon", "parrot", "lion", "monkey", "leopard"],
        columns=("class", "order", "max_speed"),
    )
    groupers = [Grouper(index_name="class"), Grouper(index_name="order")]
    groups = split_groups(df, groupers=groupers)
    assert len(groups) == 4
    assert [k for (k, _) in groups] == [
        (("class", "=", "bird"), ("order", "=", "Falconiformes")),
        (("class", "=", "bird"), ("order", "=", "Psittaciformes")),
        (("class", "=", "mammal"), ("order", "=", "Carnivora")),
        (("class", "=", "mammal"), ("order", "=", "Primates")),
    ]
    assert all(isinstance(group, pd.DataFrame) for group in [v for (_, v) in groups])

    def get_actual(key: CompositeFilter) -> pd.DataFrame:
        return next(iter([v for (k, v) in groups if k == key]))

    class_bird_order_falconiformes_expected_df = pd.DataFrame(
        [("bird", "Falconiformes", 389.0)],
        index=["falcon"],
        columns=("class", "order", "max_speed"),
    )
    pd.testing.assert_frame_equal(
        get_actual((("class", "=", "bird"), ("order", "=", "Falconiformes"))),
        class_bird_order_falconiformes_expected_df,
    )
    class_bird_order_psittaciformes_expected_df = pd.DataFrame(
        [("bird", "Psittaciformes", 24.0)],
        index=["parrot"],
        columns=("class", "order", "max_speed"),
    )
    pd.testing.assert_frame_equal(
        get_actual((("class", "=", "bird"), ("order", "=", "Psittaciformes"))),
        class_bird_order_psittaciformes_expected_df,
    )
