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
