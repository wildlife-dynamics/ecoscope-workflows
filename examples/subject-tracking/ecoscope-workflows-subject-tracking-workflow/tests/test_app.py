# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
<<<<<<< HEAD
# from-spec-sha256 = "030474a8999b732797c67f96a4e84066b843fa1b916296fe83f432ffa7d08480"
=======
# from-spec-sha256 = "a45a987fc5f35a6d3f9e1ac858aa050ef6afeca2bb96c8deda154a804dc69253"
>>>>>>> d90c2c5 (recompile)


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
