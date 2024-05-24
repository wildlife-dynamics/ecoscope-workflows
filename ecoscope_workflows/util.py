import importlib
from importlib.resources import files
from pathlib import Path
from typing import cast

from ecoscope_workflows.decorators import DistributedTask
from ecoscope_workflows.serde import gpd_from_parquet_uri


def rsplit_importable_reference(reference: str) -> list[str]:
    """Splits enclosing module (or anchor) and object name from importable reference."""
    return reference.rsplit(".", 1)


def validate_importable_reference(reference: str):
    """Without importing the reference, does the best we can to ensure that it will be importable."""
    parts = rsplit_importable_reference(reference)
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


def import_distributed_task_from_reference(
    anchor: str, func_name: str
) -> DistributedTask:
    """Import a distributed task function from an importable reference."""
    # TODO: we will need to be clear in docs about what imports are allowed at top
    # level (ecoscope_workflows, pydantic, pandera, pandas) and which imports must
    # be deferred to function body (geopandas, ecoscope itself, etc.). maybe we can
    # also enforce this programmatically.
    mod = importlib.import_module(anchor)
    func = getattr(mod, func_name)
    assert isinstance(
        func, DistributedTask
    ), f"{anchor}.{func_name} is not `@distributed`"
    return func


def _example_return_path_from_task_reference(anchor: str, func_name: str) -> Path:
    """Return the filename of the example return data for a distributed task."""
    all_files_for_anchor = files(anchor)
    all_example_return_fnames = [
        cast(Path, f)
        for f in all_files_for_anchor.iterdir()
        if cast(Path, f).suffix in (".parquet", ".json", ".html")
    ]
    example_return_fnames_for_task = [
        f
        for f in all_example_return_fnames
        if f.stem == f"{func_name.replace('_', '-')}.example-return"
    ]
    assert (
        len(example_return_fnames_for_task) == 1
    ), f"Expected 1 example return file, got {len(example_return_fnames_for_task)}"
    return example_return_fnames_for_task[0]


def load_example_return_from_task_reference(anchor: str, func_name: str):
    """Load example return data from a distributed task reference."""
    example_return_path = _example_return_path_from_task_reference(anchor, func_name)
    match example_return_path.suffix:
        case ".parquet":
            return gpd_from_parquet_uri(example_return_path.as_uri())
        case ".json":
            raise NotImplementedError("JSON example return data not yet implemented.")
        case ".html":
            raise NotImplementedError("HTML example return data not yet implemented.")
        case _:
            raise ValueError(f"No loader implemented for {example_return_path.suffix=}")
