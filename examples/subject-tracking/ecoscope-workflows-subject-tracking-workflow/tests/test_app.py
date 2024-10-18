# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "1bba0e65ec660ba6386aa5c8a7c29109ccb34607bd2f62e3aed4d8f3b2a9ef10"


from pathlib import Path

import pytest
import pydantic
from fastapi.testclient import TestClient
from ecoscope_workflows_core.testing import TestCase

from ecoscope_workflows_subject_tracking_workflow.params import Params


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
    invalid_request = client.post("/params", json={"invalid": "request"})
    assert invalid_request.status_code == 422

    response = client.post("/params", json=formdata)
    assert response.status_code == 200

    if set(formdata) != set(case.params):
        # this workflow uses task groups, so make a few extra asserts
        # task groups are not required, so these asserts are skipped
        # for workflows that simply use a flat layout
        assert set(response.json()) == set(case.params)

        with pytest.raises(pydantic.ValidationError):
            Params(**formdata)

    assert Params(**response.json()) == Params(**case.params)
