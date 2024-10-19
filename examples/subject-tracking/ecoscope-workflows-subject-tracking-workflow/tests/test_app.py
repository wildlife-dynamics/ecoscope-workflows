# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "b9febf5b3ff98ca3fd882b4f918e74114c04e0ff454b22c33ea84337b0ba9b0f"


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
    request = {"params": case.params}
    query_params = {
        "execution_mode": execution_mode,
        "mock_io": mock_io,
        "results_url": tmp_path.as_uri(),
    }
    headers = {"Content-Type": "application/json"}
    response = client.post(
        "/",
        json=request,
        params=query_params,
        headers=headers,
    )
    assert response.status_code == 200
