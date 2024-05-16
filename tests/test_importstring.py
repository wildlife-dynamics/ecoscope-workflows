import pytest

from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.importstring import import_item


def test_import_item():
    importable_reference = "ecoscope_workflows.tasks.python.analysis.calculate_time_density"
    calculate_time_density = import_item(importable_reference)

    assert isinstance(calculate_time_density, distributed)


def test_import_item_raises():
    not_importable = "this.doesnt.exist"
    with pytest.raises(ImportError):
        _ = import_item(not_importable)