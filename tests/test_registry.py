from pydantic import SecretStr
from pydantic.fields import FieldInfo

from ecoscope_workflows.registry import KnownTask, KubernetesPodOperator


def test_connections_model_fields():
    importable_reference = "ecoscope_workflows.tasks.io.get_subjectgroup_observations"
    kt = KnownTask(
        importable_reference=importable_reference,
        operator=KubernetesPodOperator(image="", name="", container_resources={}),
    )

    def _assert_equal(a, b):
        # pydantic.fields.FieldInfo does not implement __eq__, so this is a workaround
        assert set(a) == set(b)
        assert a[next(iter(a))]["type"] == b[next(iter(b))]["type"]
        a_fields = a[next(iter(a))]["fields"]
        b_fields = b[next(iter(b))]["fields"]
        assert isinstance(a_fields, dict)
        assert isinstance(b_fields, dict)
        assert set(a_fields) == set(b_fields)
        for k, v in a_fields.items():
            assert str(v) == str(b_fields[k])

    _assert_equal(
        kt.connections_model_fields,
        {
            "client": {
                "type": "EarthRangerConnection",
                "fields": {
                    "password": FieldInfo(
                        annotation=SecretStr,
                        required=True,
                        description="EarthRanger password",
                    ),
                    "server": FieldInfo(
                        annotation=str,
                        required=True,
                        description="EarthRanger API URL",
                    ),
                    "sub_page_size": FieldInfo(
                        annotation=int,
                        required=True,
                        description="Sub page size for API requests",
                    ),
                    "tcp_limit": FieldInfo(
                        annotation=int,
                        required=True,
                        description="TCP limit for API requests",
                    ),
                    "username": FieldInfo(
                        annotation=str,
                        required=True,
                        description="EarthRanger username",
                    ),
                },
            }
        },
    )


def test_known_task_parameters_jsonschema():
    importable_reference = "ecoscope_workflows.tasks.io.get_subjectgroup_observations"
    kt = KnownTask(
        importable_reference=importable_reference,
        operator=KubernetesPodOperator(image="", name="", container_resources={}),
    )
    assert kt.parameters_jsonschema() == {
        "additionalProperties": False,
        "properties": {
            "client": {
                "description": "A named EarthRanger connection.",
                "title": "Client",
                "type": "string",
            },
            "subject_group_name": {
                "title": "Subject Group Name",
                "type": "string",
                "description": "Name of EarthRanger Subject",
            },
            "include_inactive": {
                "title": "Include Inactive",
                "type": "boolean",
                "description": "Whether or not to include inactive subjects",
            },
            "since": {
                "format": "date-time",
                "title": "Since",
                "type": "string",
                "description": "Start date",
            },
            "until": {
                "format": "date-time",
                "title": "Until",
                "type": "string",
                "description": "End date",
            },
        },
        "required": [
            "client",
            "subject_group_name",
            "include_inactive",
            "since",
            "until",
        ],
        "type": "object",
    }
