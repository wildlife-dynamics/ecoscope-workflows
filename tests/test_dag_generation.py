import json
import pathlib

import pytest
import ruamel.yaml

from ecoscope_workflows.configuration import DagBuilder, TaskInstance

EXAMPLES_DIR = pathlib.Path(__file__).parent.parent / "examples"


@pytest.fixture
def time_density_tasks():
    return [
        TaskInstance(
            known_task_name="get_subjectgroup_observations",
        ),
        TaskInstance(
            known_task_name="process_relocations",
            arg_dependencies={
                "observations": "get_subjectgroup_observations_return",
            },
            arg_prevalidators={"observations": "gpd_from_parquet_uri"}
        )
    ]


@pytest.fixture
def dag_builder(time_density_tasks):
    return DagBuilder(
        name="calculate_time_density", 
        tasks=time_density_tasks,
        cache_root="gcs://my-bucket/ecoscope/cache/dag-runs"
    )


def test_yaml_config(dag_builder: DagBuilder):
    yaml = ruamel.yaml.YAML(typ='safe')
    with open(EXAMPLES_DIR / "dag-configs" / "calculate-time-density.yaml") as f:
        from_yaml = DagBuilder(**yaml.load(f))
    assert from_yaml.dag_config == dag_builder.dag_config


def test_dag_builder_generate_dag_k8s(dag_builder: DagBuilder):
    dag_str = dag_builder._generate_dag()
    
    # TODO: remove after this looks right
    with open("examples/dags/time_density_k8s.py", "w") as f:
        f.write(dag_str)
    # with open(EXAMPLES_DIR / "dags" / "calculate_time_density.py") as f:
    #     assert dag_str == f.read()


def test_dag_builder_generate_dag_script_sequential(dag_builder: DagBuilder):
    dag_builder.template = "script-sequential.jinja2"
    dag_str = dag_builder._generate_dag()

    # TODO: remove after this looks right
    with open("examples/dags/time_density_script_sequential.py", "w") as f:
        f.write(dag_str)
    # with open(EXAMPLES_DIR / "dags" / "calculate_time_density.py") as f:
    #     assert dag_str == f.read()



def test_dag_builder_dag_params_schema(dag_builder: DagBuilder):
    params = dag_builder.dag_params_schema()

    # TODO: remove after this looks right
    with open(EXAMPLES_DIR / "dags" / "time_density.json", "w") as f:
        json.dump(params, f, indent=4)
    assert "get_subjectgroup_observations" in params
    assert "process_relocations" in params

    # with open(EXAMPLES_DIR / "dags" / "calculate_time_density.json") as f:
    #     assert params == json.load(f)    
    # TODO: assert valid json schema


def test_dag_builder_dag_params_yaml_template(dag_builder: DagBuilder):
    yaml_str = dag_builder.dag_params_yaml()
    yaml = ruamel.yaml.YAML(typ='rt')
    # TODO: remove after this looks right
    with open(EXAMPLES_DIR / "dags" / "time_density.yaml", "w") as f:
        yaml.dump(yaml.load(yaml_str), f)


# def test_dag_builder(dag_builder: DagBuilder):
    # if ecoscope_server either runs (or has access to over HTTP)
    # a service that has ecoscope_workflows installed, along with
    # (for a given deployment), all user-defined tasks registered
    # in the service instance, then ecoscope_server can define tables
    # for: known_tasks, and workflows (e.g., pre-defined dags), which
    # look like: the `config` below + param export + confirmation that
    # the associated dag is available on airflow with the generated code
    # for that named dag having the same hash as for the code for the config
    # (which we can store as well). to configure a new workflow, anything
    # in the `config` below can be templated by the user on the frontend,
    # and then a POST call can be made to generate and register the dag
    # with the airflow instance. even our "default" dags can be built this
    # way.

    # TODO: on __init__, validate the following:
    #   - the dag is indeed acyclic (with graphlib.TopologicalSorter probably)
    #   - all top-level tasks are registered in `known_tasks` (type signatures
    #     of tasks themselves can be validated at registration time). note on
    #     `known_tasks` from external providers: inside the function body anything
    #     available in their associated docker image is importable, outside is
    #     a smaller subset of dependencies (the parsing dependencies), as 
    #     defined by ecoscope-workflows (they can bring their own as long as not
    #     conflicting with ecoscope-workflows requirements)
    #   - that for every dependency of every task, the specified arg name:
    #       1. actually exists on the signature of the task
    #       2. that the value given for the dependency is actually a task
    #          in the dag
    #       3. the type of the arg on the task matches the return type of
    #           the arg on the task specified as a dependency
    # `dag` here is string, needs to be dumped to airflow dags folder
    # somewhere (locally, gcs, etc.) to be discoverable + runnable
    # see note above in dependencies about re: what to include in `params`
    #   (this would be a call to TypeAdapter internally)
    # this is a jsonschema dict, also needs to be dumped somewhere useful
    # dag, params = dag_builder.generate()
