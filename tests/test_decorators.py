from dataclasses import FrozenInstanceError

import pytest

from ecoscope_workflows.decorators import task


def test_frozen_instance():
    @task
    def f(a: int) -> int:
        return a

    assert not f.validate
    with pytest.raises(FrozenInstanceError):
        f.validate = True

    f_new = f.replace(validate=True)
    assert f_new.validate


def test_call_simple():
    @task
    def f(a: int) -> int:
        return a

    assert f(1) == 1
    assert f(2) == 2


def test_call_alias_simple():
    @task
    def f(a: int) -> int:
        return a

    assert f.call(1) == 1
    assert f.call(2) == 2


def test_map_simple():
    @task
    def f(a: int) -> int:
        return a

    assert f.map("a", [1, 2, 3]) == [1, 2, 3]

    @task
    def double(a: int) -> int:
        return a * 2

    assert double.map("a", [1, 2, 3]) == [2, 4, 6]


def test_mapvalues_simple():
    @task
    def double(a: int) -> int:
        return a * 2

    keyed_input = [("h", 1), ("i", 2), ("j", 3)]
    expected_output = [("h", 2), ("i", 4), ("j", 6)]
    assert double.mapvalues("a", keyed_input) == expected_output


def test_map_args_unpacking():
    @task
    def f(a: int, b: int) -> int:
        return a + b

    assert f.map(["a", "b"], [(1, 2), (3, 4), (5, 6)]) == [3, 7, 11]


def test_mapvalues_args_unpacking():
    @task
    def f(a: int, b: int) -> int:
        return a + b

    keyed_input = [("h", (1, 2)), ("i", (3, 4)), ("j", (5, 6))]
    expected_output = [("h", 3), ("i", 7), ("j", 11)]
    with pytest.raises(
        NotImplementedError,
        match="Arg unpacking is not yet supported for `mapvalues`.",
    ):
        assert f.mapvalues(["a", "b"], keyed_input) == expected_output


def test_partial():
    @task
    def f(a: int, b: int) -> int:
        return a + b

    # make a copy first
    f_partial = f.partial(a=1)
    assert f_partial(b=2) == 3
    assert f_partial(b=3) == 4

    # or direct call with parens
    assert f.partial(a=1)(b=2) == 3
    assert f.partial(a=1)(b=3) == 4

    # or direct call with dotted call alias
    # (same as parens, just more readable)
    assert f.partial(a=1).call(b=2) == 3
    assert f.partial(a=1).call(b=3) == 4
