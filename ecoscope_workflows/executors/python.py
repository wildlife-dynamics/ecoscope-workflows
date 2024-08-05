from typing import Callable, ParamSpec, Sequence, TypeVar

from .base import Executor

P = ParamSpec("P")
R = TypeVar("R")


class PythonExecutor(Executor[P, R]):
    def call(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    def map(self, func: Callable[..., R], iterable: Sequence) -> Sequence[R]:
        mapper = map(func, iterable)
        return list(mapper)
