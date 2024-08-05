from dataclasses import FrozenInstanceError

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
        "limit_cpu": 1,
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
