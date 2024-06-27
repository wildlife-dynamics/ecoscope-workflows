from typing import Annotated, Callable

from pydantic import Field

from ecoscope_workflows.decorators import DistributedTask, distributed


@distributed
def map_reduce(
    map_function: Annotated[Callable, Field()],
    groups: Annotated[list[tuple[str, ...]], Field()],
    reducer: Annotated[DistributedTask, Field()],
    # reducer_kwargs: Annotated[dict, Field(default_factory=dict)],
):
    import lithops

    # Configure the compute backend (local, cloud, etc.) with a configuration file:
    # https://lithops-cloud.github.io/docs/source/configuration.html#configuration-file
    fexec = lithops.FunctionExecutor()

    fexec.map_reduce(
        map_function=map_function,
        map_iterdata=groups,
        reduce_function=reducer,
        # extra_args_reduce=(reducer_kwargs,),
    )
    return fexec.get_result()
