from ecoscope_workflows.core.registry import KnownTask


def test_known_task_parameters_jsonschema():
    importable_reference = (
        "ecoscope_workflows.ext.ecoscope.tasks.io.get_subjectgroup_observations"
    )
    kt = KnownTask(importable_reference=importable_reference)
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
            "include_inactive": {
                "default": True,
                "title": "Include Inactive",
                "type": "boolean",
                "description": "Whether or not to include inactive subjects",
            },
        },
        "required": ["client", "subject_group_name", "since", "until"],
        "type": "object",
    }
