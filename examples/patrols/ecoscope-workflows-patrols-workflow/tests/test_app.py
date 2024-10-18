# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "16f756386e14612d875d95d9640b778f31eb33ad9db3f241ab4ce1fe3aecc4b6"


from pathlib import Path

import pytest
import pydantic
from fastapi.testclient import TestClient
from ecoscope_workflows_core.testing import TestCase

from ecoscope_workflows_patrols_workflow.params import Params


def test_run(
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


def test_get_params(client: TestClient):
    response = client.get("/params")
    assert response.status_code == 200
    assert set(list(response.json())) == {
        "title",
        "properties",
        "$defs",
        "additionalProperties",
        "uiSchema",
    }


def test_validate_formdata(client: TestClient, case: TestCase, formdata: dict):
    invalid_request = client.post("/params", json=case.params)
    assert invalid_request.status_code == 422

    response = client.post("/params", json=formdata)
    assert response.status_code == 200

    assert set(formdata) != set(case.params)
    assert set(response.json()) == set(case.params)

    with pytest.raises(pydantic.ValidationError):
        Params(**formdata)

    assert Params(**response.json()) == Params(**case.params)
