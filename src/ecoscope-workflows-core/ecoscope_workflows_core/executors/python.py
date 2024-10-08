from typing import Callable, Iterable, Sequence

from .base import SyncExecutor, P, R


class PythonExecutor(SyncExecutor):
    def call(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    def map(self, func: Callable[..., R], iterable: Iterable[R]) -> Sequence[R]:
        mapper = map(func, iterable)
        return list(mapper)
