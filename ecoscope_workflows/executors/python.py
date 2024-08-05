from typing import Callable, ParamSpec, Iterable, Sequence, TypeVar

from .base import Executor

P = ParamSpec("P")
R = TypeVar("R")
K = TypeVar("K")
V = TypeVar("V")


class PythonExecutor(Executor[P, R, K, V]):
    def call(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    def map(
        self, func: Callable[..., R], iterable: Iterable[dict[str, V]]
    ) -> Sequence[R]:
        mapper = map(func, iterable)
        return list(mapper)

    def mapvalues(
        self,
        func: Callable[..., tuple[K, R]],
        iterable: Iterable[dict[K, dict[str, V]]],
    ) -> Sequence[tuple[K, R]]:
        mapper = map(func, iterable)
        return list(mapper)
