import pytest
from fastapi.testclient import TestClient

from ecoscope_workflows_core.testing import TestCase


@pytest.mark.parametrize("execution_mode", ["async", "sequential"])
@pytest.mark.parametrize("mock_io", [True], ids=["mock-io"])
def test_app(client: TestClient, execution_mode: str, mock_io: bool, case: TestCase):
    response = client.post(
        "/",
        json={
            "execution_mode": execution_mode,
            "mock_io": mock_io,
            "params": case.params,
            "results_url": ...,
        },
    )
    assert response.status_code == 200
