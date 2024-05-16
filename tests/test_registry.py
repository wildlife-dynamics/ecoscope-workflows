from ecoscope_workflows.registry import KnownTask, KubernetesPodOperator


def test_known_task_parameters_jsonschema():
    importable_reference = "ecoscope_workflows.tasks.python.io.get_subjectgroup_observations"
    kt = KnownTask(
        importable_reference=importable_reference,
        operator=KubernetesPodOperator(image="", name="", container_resources={})
    )
    assert kt.parameters_jsonschema == {
        'additionalProperties': False,
        'properties': {
            'server': {'title': 'Server'},
            'username': {'title': 'Username'},
            'password': {'title': 'Password'},
            'tcp_limit': {'title': 'Tcp Limit'},
            'sub_page_size': {'title': 'Sub Page Size'},
            'subject_group_name': {'title': 'Subject Group Name'},
            'include_inactive': {'title': 'Include Inactive'},
            'since': {'title': 'Since'},
            'until': {'title': 'Until'},
        },
        'type': 'object',
    }
