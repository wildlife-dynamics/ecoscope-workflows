import importlib

from ecoscope_workflows.decorators import distributed


def _rsplit_importable_reference(reference: str) -> list[str]:
    """Splits enclosing module and object name from importable reference."""
    return reference.rsplit(".", 1)


def _validate_importable_reference(reference: str):
    """Without importing the reference, does the best we can to ensure that it will be importable."""
    parts = _rsplit_importable_reference(reference)
    assert (
        len(parts) == 2
    ), f"{reference} is not a valid importable reference, must be a dotted string."
    assert (
        parts[1].isidentifier()
    ), f"{parts[1]} is not a valid Python identifier, it will not be importable."
    assert all(
        [module_part.isidentifier() for module_part in parts[0].split(".")]
    ), f"{parts[0]} is not a valid Python module path, it will not be importable."
    return reference


def import_distributed_task_from_reference(anchor: str, func_name: str) -> distributed:
    """Import a distributed task function from an importable reference."""
    # TODO: we will need to be clear in docs about what imports are allowed at top
    # level (ecoscope_workflows, pydantic, pandera, pandas) and which imports must
    # be deferred to function body (geopandas, ecoscope itself, etc.). maybe we can
    # also enforce this programmatically.
    mod = importlib.import_module(anchor)
    func = getattr(mod, func_name)
    assert isinstance(func, distributed), f"{anchor}.{func_name} is not `@distributed`"
    return func
