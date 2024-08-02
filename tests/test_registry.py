from ecoscope_workflows.registry import KnownTask, OperatorKws


def test_known_task_parameters_jsonschema():
    # test
    importable_reference = "ecoscope_workflows.tasks.io.get_subjectgroup_observations"
    kt = KnownTask(
        importable_reference=importable_reference,
        operator_kws=OperatorKws(image="", container_resources={}),
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
