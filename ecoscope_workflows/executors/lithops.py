from dataclasses import dataclass, field
from typing import Callable, Generic, Iterable, Sequence

try:
    from lithops import FunctionExecutor
    from lithops.future import ResponseFuture
    from lithops.utils import FuturesList
except ImportError:
    raise ImportError(
        "Please install the `lithops` package to use the `LithopsExecutor`."
    )

from .base import Executor, P, R


class GenericResponseFuture(ResponseFuture, Generic[R]):
    def result(self, *args, **kwargs) -> R:
        return super().result(*args, **kwargs)


class GenericFuturesList(FuturesList, Generic[R]):
    def get_result(self, *args, **kwargs) -> Sequence[R]:
        return super().get_result(*args, **kwargs)


@dataclass
class LithopsExecutor(Executor):
    fexec: FunctionExecutor = field(default_factory=FunctionExecutor)

    def call(
        self,
        func: Callable[P, R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> GenericResponseFuture[R]:
        if args:
            return self.fexec.call_async(func, data=args)
        if args and kwargs:
            raise ValueError(
                "Cannot pass both args and kwargs to `LithopsExecutor.call`."
            )
        return self.fexec.call_async(func, data=kwargs)

    def map(
        self,
        func: Callable[..., R],
        iterable: Iterable[R],
    ) -> GenericFuturesList[R]:
        return self.fexec.map(func, iterable)
