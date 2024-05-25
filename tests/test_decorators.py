from dataclasses import FrozenInstanceError
from typing import Annotated

import pytest

from ecoscope_workflows.decorators import distributed


def test_call_simple_default_operator_kws():
    @distributed
    def f(a: int, b: int) -> int:
        return a + b

    assert f.func(1, 2) == 3
    assert f(1, 2) == 3
    assert f.operator_kws.image == "ecoscope-workflows:latest"
    assert f.operator_kws.container_resources == {
        "request_memory": "128Mi",
        "request_cpu": "500m",
        "limit_memory": "500Mi",
        "limit_cpu": 2,
    }


def test_call_simple_custom_operator_kws():
    @distributed(
        image="my-custom-image:abc123",
        container_resources={
            "request_memory": "400M",
            "request_cpu": 16,
            "limit_memory": "800M",
            "limit_cpu": 32,
        },
    )
    def f(a: int, b: int) -> int:
        return a + b

    assert f.func(1, 2) == 3
    assert f(1, 2) == 3
    assert f.operator_kws.image == "my-custom-image:abc123"
    assert f.operator_kws.container_resources == {
        "request_memory": "400M",
        "request_cpu": 16,
        "limit_memory": "800M",
        "limit_cpu": 32,
    }


def test_frozen_instance():
    @distributed
    def f(a: int) -> int:
        return a

    assert not f.validate
    with pytest.raises(FrozenInstanceError):
        f.validate = True

    f_new = f.replace(validate=True)
    assert f_new.validate


def test_arg_prevalidators():
    @distributed
    def f(a: Annotated[int, "some metadata field"]) -> int:
        return a

    def a_prevalidator(x):
        return x + 1

    f_new = f.replace(arg_prevalidators={"a": a_prevalidator})
    # the prevalidator's behavior
    assert a_prevalidator(1) == 2
    # without `validate=True` we still get normal behavior from the function itself
    assert f_new(1) == 1
    # only when we set validate=True do we finally see the prevalidator is invoked
    assert f_new.replace(validate=True)(1) == 2


def test_return_postvalidator():
    @distributed
    def f(a) -> Annotated[int, "some metadata field"]:
        return a

    assert f(4) == 4

    def postvalidator(x):
        return x + 1

    # note that the postvalidator will not be invoked unless `validate=True`
    f_new = f.replace(return_postvalidator=postvalidator, validate=True)
    assert f_new(4) == 5
