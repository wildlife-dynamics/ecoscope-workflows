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
