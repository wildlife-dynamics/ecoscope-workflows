# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "8a3657e3ebaa4bfbe1bbaaac414f150f77aaa86dfa1e7d1d71c3b10235974666"


from pathlib import Path

import pytest
import pydantic
from fastapi.testclient import TestClient
from ecoscope_workflows_core.testing import TestCase

from ecoscope_workflows_patrols_workflow.params import Params
from ecoscope_workflows_patrols_workflow.formdata import FormData


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
    response = client.get("/rjsf")
    assert response.status_code == 200
    assert set(list(response.json())) == {
        "title",
        "properties",
        "$defs",
        "additionalProperties",
        "uiSchema",
    }


def test_validate_formdata(client: TestClient, case: TestCase, formdata: dict):
    invalid_request = client.post("/formdata-to-params", json={"invalid": "request"})
    assert invalid_request.status_code == 422

    response = client.post("/formdata-to-params", json=formdata)
    assert response.status_code == 200

    assert set(response.json()) == set(case.params)

    if set(formdata) != set(case.params):
        # this workflow uses task groups, so make one other assert
        # task groups are not required, so these asserts are skipped
        # for workflows that simply use a flat layout

        with pytest.raises(pydantic.ValidationError):
            Params(**formdata)

    assert Params(**response.json()) == Params(**case.params)


def test_generate_nested_params(client: TestClient, case: TestCase, formdata: dict):
    response = client.post("/params-to-formdata", json=case.params)
    assert response.status_code == 200

    assert FormData(**response.json()) == FormData(**formdata)


def test_round_trip(client: TestClient, case: TestCase, formdata: dict):
    generate_params_response = client.post(
        "/params-to-formdata", json=case.model_dump().get("params")
    )
    assert generate_params_response.status_code == 200
    assert generate_params_response.json == formdata

    validate_response = client.post(
        "/formdata-to-params", json=generate_params_response.json()
    )
    assert validate_response.status_code == 200

    assert set(validate_response.json()) == set(case.params)
    assert Params(**validate_response.json()) == Params(**case.params)
