from fastapi.testclient import TestClient

from ecoscope_workflows_mode_map_workflow.app import app

client = TestClient(app)


def test_run():
    response = client.post(
        "/",
        json={
            "entrypoint": "ecoscope-workflows-mode-map-workflow",
            "execution_mode": "sequential",
            "mock_io": True,
            "case_name": "case",
        },
    )
    assert response.status_code == 200
