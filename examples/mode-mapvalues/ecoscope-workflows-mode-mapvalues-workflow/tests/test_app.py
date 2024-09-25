from pathlib import Path

from fastapi.testclient import TestClient

from ecoscope_workflows_core.testing import TestCase


def test_app(
    client: TestClient,
    execution_mode: str,
    mock_io: bool,
    case: TestCase,
    tmp_path: Path,
):
    response = client.post(
        "/",
        json={
            "params": case.params,
            "execution_mode": execution_mode,
            "mock_io": mock_io,
            "results_url": tmp_path.as_posix(),
        },
    )
    assert response.status_code == 200
