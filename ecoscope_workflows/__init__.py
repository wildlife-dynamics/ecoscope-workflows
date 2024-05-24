import types

# from importlib import import_module
from importlib.metadata import entry_points

# from importlib.util import find_spec
from inspect import getmembers, ismodule

from ecoscope_workflows.decorators import distributed
# from ecoscope_workflows.registry import known_tasks, register_known_task


def recurse_into_tasks(module: types.ModuleType):
    """Recursively yield `@distributed` task names from the given module (i.e. package)."""
    for name, obj in [
        m for m in getmembers(module) if not m[0].startswith(("__", "_"))
    ]:
        if isinstance(obj, distributed):
            yield name  # FIXME: return full `importable_reference`
        elif ismodule(obj):
            yield from recurse_into_tasks(obj)
        else:
            raise ValueError(f"Unexpected member {obj} in module {module}")


def process_entries():
    eps = entry_points()
    assert hasattr(eps, "select")  # Python >= 3.10
    ecoscope_workflows_eps = eps.select(group="ecoscope_workflows")
    for ep in ecoscope_workflows_eps:
        # a bit redundant with `util.import_distributed_task_from_reference`
        root_pkg_name, tasks_pkg_name = ep.value.rsplit(".", 1)
        assert "." not in root_pkg_name, (
            "Tasks must be top-level in root (e.g. `pkg.tasks`, not `pkg.foo.tasks`). "
            f"Got: `{root_pkg_name}.{tasks_pkg_name}`"
        )
        # root = import_module(root_pkg_name)
        # tasks = getattr(root, tasks_pkg_name)  # circular import
        # members = [m for m in getmembers(tasks) if not m[0].startswith("__")]

        # register_known_task(task.load())
        # breakpoint()


process_entries()
# print(known_tasks)
