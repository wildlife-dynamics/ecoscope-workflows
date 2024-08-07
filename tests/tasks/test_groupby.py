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
    groupers = set_groupers(["class", "order"])
    assert len(groupers) == 2
    assert all(isinstance(g, Grouper) for g in groupers)
    assert groupers[0].index_name == "class"
    assert groupers[1].index_name == "order"


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
    groupers = ["class", "order"]
    groups = split_groups(df, groupers=groupers)
    assert len(groups) == 4
    assert list(groups) == [
        (("class", "=", "bird"), ("order", "=", "Falconiformes")),
        (("class", "=", "bird"), ("order", "=", "Psittaciformes")),
        (("class", "=", "mammal"), ("order", "=", "Carnivora")),
        (("class", "=", "mammal"), ("order", "=", "Primates")),
    ]
    assert all(isinstance(group, pd.DataFrame) for group in groups.values())
    class_bird_order_falconiformes_expected_df = pd.DataFrame(
        [("bird", "Falconiformes", 389.0)],
        index=["falcon"],
        columns=("class", "order", "max_speed"),
    )
    pd.testing.assert_frame_equal(
        groups[(("class", "=", "bird"), ("order", "=", "Falconiformes"))],
        class_bird_order_falconiformes_expected_df,
    )
    class_bird_order_psittaciformes_expected_df = pd.DataFrame(
        [("bird", "Psittaciformes", 24.0)],
        index=["parrot"],
        columns=("class", "order", "max_speed"),
    )
    pd.testing.assert_frame_equal(
        groups[(("class", "=", "bird"), ("order", "=", "Psittaciformes"))],
        class_bird_order_psittaciformes_expected_df,
    )
