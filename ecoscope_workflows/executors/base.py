from abc import ABC, abstractmethod
from typing import Callable, Generic, Iterable, ParamSpec, Sequence, TypeVar


P = ParamSpec("P")
R = TypeVar("R")


class Executor(ABC, Generic[P, R]):
    @abstractmethod
    def call(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        pass

    @abstractmethod
    def map(self, func: Callable[..., R], iterable: Iterable) -> Sequence[R]:
        pass
