from ecoscope_workflows.compiler import TaskInstance
from ecoscope_workflows.registry import KnownTask, known_tasks


def test_task_instance_known_task_parsing():
    task_name = "get_subjectgroup_observations"
    ti = TaskInstance(known_task_name=task_name)
    assert isinstance(ti.known_task, KnownTask)
    assert ti.known_task == known_tasks[task_name]


def test_dag_compiler_from_spec(): ...


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
