import functools
from dataclasses import dataclass, field
from typing import Callable, Iterable, Sequence

try:
    from lithops import FunctionExecutor
    from lithops.future import ResponseFuture
    from lithops.utils import FuturesList
except ImportError:
    raise ImportError(
        "Please install the `lithops` package to use the `LithopsExecutor`."
    )

from .base import AsyncExecutor, Future, FutureSequence, P, R, T


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


def wrap(func) -> Callable[P, R]:
    class wrapped_func:
        def __init__(self, func):
            self.func = func

        def __call__(self, *args, **kwargs):
            return self.func(**kwargs)

    wrapper = wrapped_func(func)
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
        futures = self.fexec.map(wrap(func), iterable)
        return LithopsFuturesSequence(futures=futures)
