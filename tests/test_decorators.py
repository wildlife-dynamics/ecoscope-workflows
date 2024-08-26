from dataclasses import FrozenInstanceError

import pytest

from ecoscope_workflows.decorators import task


def test_frozen():
    @task
    def f(a: int, b: int) -> int:
        return a + b

    with pytest.raises(FrozenInstanceError, match="cannot assign to field 'executor'"):
        f.executor = None

    with pytest.raises(FrozenInstanceError, match="cannot assign to field 'tags'"):
        f.tags = None

    with pytest.raises(FrozenInstanceError, match="cannot assign to field 'func'"):
        f.func = None


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


def test_partial_call():
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


def test_partial_map():
    @task
    def f(a: int, b: int) -> int:
        return a + b

    assert f.partial(a=1).map("b", [2, 3]) == [3, 4]
    assert f.partial(a=1).map("b", [4, 5]) == [5, 6]


def test_partial_mapvalues():
    @task
    def f(a: int, b: int) -> int:
        return a + b

    assert f.partial(a=1).mapvalues("b", [("h", 2), ("i", 3)]) == [("h", 3), ("i", 4)]


def test_partial_repeated_args_raises():
    @task
    def f(a: int, b: int) -> int:
        return a + b

    # we just follow functools.partial behavior here,
    # so kwarg overrides are allowed
    assert f.partial(a=1).call(a=2, b=3) == 5
    # but arg overrides are not allowed
    with pytest.raises(TypeError, match="got multiple values for argument 'a'"):
        f.partial(a=1).call(2, b=3)


def test_validate():
    @task
    def f(a: int) -> int:
        return a

    assert f.validate().call(1) == 1
    assert f.validate().call(2) == 2

    # no parsing without validate
    assert f("1") == "1"
    assert f("2") == "2"

    # with validate, we get input parsing
    assert f.validate().call("1") == 1
    assert f.validate().call("2") == 2


def test_validate_partial_chain():
    @task
    def f(a: int) -> int:
        return a

    assert f.validate().partial(a="1").call() == 1


def test_partial_validate_chain():
    @task
    def f(a: int) -> int:
        return a

    assert f.partial(a="1").validate().call() == 1
