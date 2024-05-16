from ecoscope_workflows.configuration import DagBuilder, TaskInstance

time_density_tasks = [
    TaskInstance(
        known_task_name="get_earthranger_subjectgroup_observations",
    ),
    TaskInstance(
        known_task_name="process_relocations",
        arg_dependencies={
            "observations": "get_earthranger_subjectgroup_observations_return",
        },
        arg_prevalidators={"observations": "gpd_from_parquet_uri"}
    )
]


def test_dag_builder_generate_dag():
    db = DagBuilder(
        name="calculate_time_density", 
        tasks=time_density_tasks,
        cache_root="gcs://my-bucket/ecoscope/cache/dag-runs"
    )
    dag_str = db._generate_dag()
    
    # TODO: remove after this looks right
    with open("examples/dags/calculate_time_density.py", "w") as f:
        f.write(dag_str)


def test_dag_builder():
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
    config = {
        "dag": {...},  # @dag-level kwargs
        "tasks": [
            dict(
                name="importable.path.to.function",
                dependencies={
                    "arg_name_on_this_task": "another.task.in_this_dag",
                }
                # we assume anything *not* listed as a dependency will
                # be passed as a DAG Param at invocation time, and therefore
                # must be included in the return of DagBuilder.get_params().
            ),
            dict(
                name="another.task.in_this_dag",
            )
        ]
    }
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
    db = DagBuilder()
    # `dag` here is string, needs to be dumped to airflow dags folder
    # somewhere (locally, gcs, etc.) to be discoverable + runnable
    # see note above in dependencies about re: what to include in `params`
    #   (this would be a call to TypeAdapter internally)
    # this is a jsonschema dict, also needs to be dumped somewhere useful
    dag, params = db.generate()
