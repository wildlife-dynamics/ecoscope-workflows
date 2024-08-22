from abc import ABC, abstractmethod
from typing import Callable, Generic, ParamSpec, Iterable, Sequence, TypeVar

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class SyncExecutor(ABC, Generic[P, R]):
    @abstractmethod
    def call(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        pass

    @abstractmethod
    def map(self, func: Callable[..., R], iterable: Iterable[T]) -> Sequence[R]:
        pass


class Future(ABC, Generic[R]):
    @abstractmethod
    def gather(self, *args, **kwargs) -> R:
        pass


class FutureSequence(ABC, Generic[R]):
    @abstractmethod
    def gather(self, *args, **kwargs) -> Sequence[R]:
        pass


class AsyncExecutor(ABC, Generic[P, R]):
    @abstractmethod
    def call(
        self,
        func: Callable[P, R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Future[R]:
        pass

    @abstractmethod
    def map(
        self,
        func: Callable[..., R],
        iterable: Iterable[T],
    ) -> FutureSequence[R]:
        pass


class mapvalues_wrapper(Generic[K, V, R]):
    def __init__(self, func):
        self.func = func

    def __call__(self, kv: tuple[K, V]) -> tuple[K, R]:
        key, argvalue = kv
        return key, self.func(**argvalue)
