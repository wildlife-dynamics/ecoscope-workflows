from typing import Annotated

from pydantic import Field

from ecoscope_workflows.decorators import DistributedTask, distributed


@distributed
def map_reduce(
    groups: Annotated[list[tuple[str, ...]], Field()],
    # lets asssume that when we call map_reduce, we have already set the
    # arg_prevalidators and return_postvalidator for the mappers and reducer
    # so by the time lithops sees them, they are ready to call
    mappers: Annotated[list[tuple[DistributedTask, dict]], Field()],
    reducer: Annotated[DistributedTask, Field()],
    reducer_kwargs: Annotated[dict, Field(default_factory=dict)],
):
    import lithops

    # Configure the compute backend (local, cloud, etc.) with a configuration file:
    # https://lithops-cloud.github.io/docs/source/configuration.html#configuration-file
    fexec = lithops.FunctionExecutor()

    def fused_mapper(element):
        for i, (mapper, kwargs) in enumerate(mappers):
            if i == 0:
                result = mapper(element, **kwargs)
            else:
                result = mapper(result, **kwargs)
        return result

    fexec.map_reduce(
        map_function=fused_mapper,
        map_iterdata=groups,
        reduce_function=reducer,
        extra_args_reduce=reducer_kwargs,
    )
    return fexec.get_result()
