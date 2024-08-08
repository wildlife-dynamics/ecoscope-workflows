from abc import ABC, abstractmethod
from typing import Callable, Generic, Iterable, Sequence

from ecoscope_workflows.typevars import P, R, K, V


class Executor(ABC, Generic[P, R, K, V]):
    @abstractmethod
    def call(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        pass

    @abstractmethod
    def map(
        self, func: Callable[..., R], iterable: Iterable[dict[str, V]]
    ) -> Sequence[R]:
        pass

    @abstractmethod
    def mapvalues(
        self,
        func: Callable[..., tuple[K, R]],
        iterable: Iterable[tuple[K, dict[str, V]]],
    ) -> Sequence[tuple[K, R]]:
        pass
