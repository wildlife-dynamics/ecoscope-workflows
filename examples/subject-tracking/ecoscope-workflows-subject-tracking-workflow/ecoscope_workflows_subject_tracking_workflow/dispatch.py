# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
<<<<<<< HEAD
# from-spec-sha256 = "030474a8999b732797c67f96a4e84066b843fa1b916296fe83f432ffa7d08480"
=======
# from-spec-sha256 = "a45a987fc5f35a6d3f9e1ac858aa050ef6afeca2bb96c8deda154a804dc69253"
>>>>>>> d90c2c5 (recompile)


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
