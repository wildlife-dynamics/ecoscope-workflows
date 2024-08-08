from typing import Callable, Iterable, Sequence

from ecoscope_workflows.typevars import P, R, K, V
from .base import Executor


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
        iterable: Iterable[tuple[K, dict[str, V]]],
    ) -> Sequence[tuple[K, R]]:
        mapper = map(func, iterable)
        return list(mapper)
