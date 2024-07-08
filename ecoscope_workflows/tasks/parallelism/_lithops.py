from typing import Annotated, Callable

from pydantic import Field

from ecoscope_workflows.decorators import distributed


@distributed
def map_reduce(
    map_function: Annotated[Callable, Field()],
    groups: Annotated[list[tuple[str, ...]], Field()],
    reduce_function: Annotated[Callable, Field()],
    retries: Annotated[int, Field()] = 4,
):
    import lithops
    # from lithops.retries import RetryingFunctionExecutor

    # Configure the compute backend (local, cloud, etc.) with a configuration file:
    # https://lithops-cloud.github.io/docs/source/configuration.html#configuration-file
    fexec = lithops.FunctionExecutor()

    # fexec.map_reduce(
    # with RetryingFunctionExecutor(fexec) as executor:
    fexec.map(
        map_function=map_function,
        map_iterdata=groups,
        # retries=retries,
        # reduce_function=reduce_function,
        # spawn_reducer=100,
    )
    outputs = fexec.get_result()
    # done, pending = executor.wait(futures, throw_except=True)
    # assert len(pending) == 0
    # outputs = set(f.result() for f in done)

    return outputs
