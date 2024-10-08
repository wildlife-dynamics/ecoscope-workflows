# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "748252e8fb420e7edc39e0b05c8793c569ddb0fed5f92830889f0dcebdb72be1"

from ecoscope_workflows_core.tasks.results import DashboardJson

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
) -> DashboardJson:
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
