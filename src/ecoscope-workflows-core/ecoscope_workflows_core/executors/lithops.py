import functools
import inspect
from dataclasses import dataclass, field
from typing import Callable, Iterable, Sequence

try:
    from lithops import FunctionExecutor  # type: ignore[import-untyped]
    from lithops.future import ResponseFuture  # type: ignore[import-untyped]
    from lithops.utils import FuturesList  # type: ignore[import-untyped]
except ImportError:
    raise ImportError(
        "Please install the `lithops` package to use the `LithopsExecutor`."
    )

from .base import AsyncExecutor, Future, FutureSequence, mapvalues_wrapper, P, R, T


@dataclass(frozen=True)
class LithopsFuture(Future[R]):
    future: ResponseFuture

    def gather(self, *args, **kwargs) -> R:
        return self.future.result(*args, **kwargs)


@dataclass(frozen=True)
class LithopsFuturesSequence(FutureSequence[R]):
    futures: FuturesList

    def gather(self, *args, **kwargs) -> Sequence[R]:
        return self.futures.get_result(*args, **kwargs)


def _create_custom_signature(partial_func: functools.partial) -> inspect.Signature:
    # workaround for lithops inspect behavior; TODO: raise upstream issue on lithops
    original_sig = inspect.signature(partial_func.func)
    new_params = [
        param
        for name, param in original_sig.parameters.items()
        if name not in partial_func.keywords
    ]
    return original_sig.replace(parameters=new_params)


def wrap(func) -> Callable[P, R]:
    if isinstance(func, functools.partial):
        func.__signature__ = _create_custom_signature(func)  # type: ignore[attr-defined]

    class wrapped_func:
        def __init__(self, func):
            self.func = func

        def __call__(self, *args, **kwargs):
            return self.func(**kwargs)

    wrapper = wrapped_func(func)
    if isinstance(func, mapvalues_wrapper):
        functools.update_wrapper(wrapper, func.__call__)
    else:
        functools.update_wrapper(wrapper, func)
    return wrapper


@dataclass
class LithopsExecutor(AsyncExecutor):
    fexec: FunctionExecutor = field(default_factory=FunctionExecutor)

    def call(
        self,
        func: Callable[P, R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> LithopsFuture[R]:
        if args:
            raise NotImplementedError(
                "Only keyword arguments are currently supported by `LithopsExecutor.call`."
            )
        future = self.fexec.call_async(wrap(func), data=kwargs)
        return LithopsFuture(future=future)

    def map(
        self,
        func: Callable[..., R],
        iterable: Iterable[T],
    ) -> LithopsFuturesSequence[R]:
        if isinstance(func, mapvalues_wrapper):
            iterdata = [{"kv": e} for e in iterable]
        else:
            iterdata = iterable  # type: ignore[assignment]
        futures = self.fexec.map(wrap(func), iterdata)
        return LithopsFuturesSequence(futures=futures)
