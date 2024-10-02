# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "7f7a2953093d602c7a7746ca4822e4f6c3498150d973f09f090ad62a8b580361"


from typing import Any

from .dags import (
    run_async,
    run_async_mock_io,
    run_sequential,
    run_sequential_mock_io,
)
from .params import Params


def dispatch(
    execution_mode: str,  # TODO: literal type
    mock_io: bool,
    params: Params,
) -> Any:  # TODO: Dynamically define the return type
    match execution_mode, mock_io:
        case ("async", True):
            result = run_async_mock_io(params=params)
        case ("async", False):
            result = run_async(params=params)
        case ("sequential", True):
            result = run_sequential_mock_io(params=params)
        case ("sequential", False):
            result = run_sequential(params=params)
        case _:
            raise ValueError(f"Invalid execution mode: {execution_mode}")

    return result
