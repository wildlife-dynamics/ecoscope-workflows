from typing import Annotated, Callable

from pydantic import Field

from ecoscope_workflows.decorators import distributed


@distributed
def map_reduce(
    map_function: Annotated[Callable, Field()],
    groups: Annotated[list[tuple[str, ...]], Field()],
    reduce_function: Annotated[Callable, Field()],
):
    import lithops

    # Configure the compute backend (local, cloud, etc.) with a configuration file:
    # https://lithops-cloud.github.io/docs/source/configuration.html#configuration-file
    fexec = lithops.FunctionExecutor()

    fexec.map_reduce(
        map_function=map_function,
        map_iterdata=groups,
        reduce_function=reduce_function,
    )
    return fexec.get_result()
