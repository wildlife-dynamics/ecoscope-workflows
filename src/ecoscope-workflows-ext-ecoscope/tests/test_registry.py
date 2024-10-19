from ecoscope_workflows_core.registry import KnownTask


def test_known_task_parameters_jsonschema():
    importable_reference = (
        "ecoscope_workflows_ext_ecoscope.tasks.io.get_subjectgroup_observations"
    )
    kt = KnownTask(importable_reference=importable_reference)
    assert kt.parameters_jsonschema() == {
        "$defs": {
            "TimeRange": {
                "properties": {
                    "since": {
                        "format": "date-time",
                        "title": "Since",
                        "type": "string",
                    },
                    "until": {
                        "format": "date-time",
                        "title": "Until",
                        "type": "string",
                    },
                    "time_format": {
                        "default": "%d %b %Y %H:%M:%S %Z",
                        "title": "Time Format",
                        "type": "string",
                    },
                },
                "required": ["since", "until"],
                "title": "TimeRange",
                "type": "object",
            }
        },
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
            "time_range": {
                "$ref": "#/$defs/TimeRange",
                "title": "Time Range",
                "description": "Time range filter",
            },
            "include_inactive": {
                "default": True,
                "title": "Include Inactive",
                "type": "boolean",
                "description": "Whether or not to include inactive subjects",
            },
        },
        "required": ["client", "subject_group_name", "time_range"],
        "type": "object",
    }
