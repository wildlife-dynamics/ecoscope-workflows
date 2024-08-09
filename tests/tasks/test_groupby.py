import numpy as np
import pandas as pd

import pytest

from ecoscope_workflows.indexes import CompositeFilter, IndexName, IndexValue
from ecoscope_workflows.tasks.groupby import groupbykey, set_groupers, split_groups
from ecoscope_workflows.tasks.groupby._groupby import (
    Grouper,
    KeyedIterableOfAny,
    _groupkey_to_composite_filter,
)


def getvalue(key: CompositeFilter, groups: KeyedIterableOfAny) -> pd.DataFrame:
    """Convenience function to get the values for a given key in a KeyedIterable."""
    return next(iter([v for (k, v) in groups if k == key]))


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

    class_bird_order_falconiformes_expected_df = pd.DataFrame(
        [("bird", "Falconiformes", 389.0)],
        index=["falcon"],
        columns=("class", "order", "max_speed"),
    )
    pd.testing.assert_frame_equal(
        getvalue((("class", "=", "bird"), ("order", "=", "Falconiformes")), groups),
        class_bird_order_falconiformes_expected_df,
    )
    class_bird_order_psittaciformes_expected_df = pd.DataFrame(
        [("bird", "Psittaciformes", 24.0)],
        index=["parrot"],
        columns=("class", "order", "max_speed"),
    )
    pd.testing.assert_frame_equal(
        getvalue((("class", "=", "bird"), ("order", "=", "Psittaciformes")), groups),
        class_bird_order_psittaciformes_expected_df,
    )


def test_groupbykey():
    falcon = pd.DataFrame([("falcon", 389.0)], index=["falcon"])
    parrot = pd.DataFrame([("parrot", 24.0)], index=["parrot"])
    lion = pd.DataFrame([("lion", 80.2)], index=["lion"])
    monkey = pd.DataFrame([("monkey", np.nan)], index=["monkey"])

    iterable_0 = [
        ((("class", "=", "bird"),), falcon),
        ((("class", "=", "mammal"),), lion),
    ]
    iterable_1 = [
        ((("class", "=", "bird"),), parrot),
        ((("class", "=", "mammal"),), monkey),
    ]
    output = groupbykey(iterables=[iterable_0, iterable_1])

    # bird and mammal groups are combined
    assert output == [
        ((("class", "=", "bird"),), [falcon, parrot]),
        ((("class", "=", "mammal"),), [lion, monkey]),
    ]
