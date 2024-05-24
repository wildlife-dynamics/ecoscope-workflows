from ecoscope_workflows.registry import KnownTask, KubernetesPodOperator


def test_known_task_parameters_jsonschema():
    importable_reference = "ecoscope_workflows.tasks.io.get_subjectgroup_observations"
    kt = KnownTask(
        importable_reference=importable_reference,
        operator=KubernetesPodOperator(image="", name="", container_resources={}),
    )
    assert kt.parameters_jsonschema() == {
        "additionalProperties": False,
        "properties": {
            "server": {
                "title": "Server",
                "type": "string",
                "description": "URL for EarthRanger API",
            },
            "username": {
                "title": "Username",
                "type": "string",
                "description": "EarthRanger username",
            },
            "password": {
                "title": "Password",
                "type": "string",
                "description": "EarthRanger password",
            },
            "tcp_limit": {
                "title": "Tcp Limit",
                "type": "integer",
                "description": "TCP limit for EarthRanger API requests",
            },
            "sub_page_size": {
                "title": "Sub Page Size",
                "type": "integer",
                "description": "Sub page size for EarthRanger API requests",
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
            "server",
            "username",
            "password",
            "tcp_limit",
            "sub_page_size",
            "subject_group_name",
            "include_inactive",
            "since",
            "until",
        ],
        "type": "object",
    }
