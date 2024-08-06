import functools
from dataclasses import FrozenInstanceError, dataclass, field, replace
from typing import Callable, Generic, Sequence, cast, overload

from pydantic import validate_call

from ecoscope_workflows.typevars import P, R, K, V
from ecoscope_workflows.executors import Executor
from ecoscope_workflows.executors.python import PythonExecutor


@dataclass
class Task(Generic[P, R, K, V]):
    """ """

    func: Callable[P, R]
    executor: Executor[P, R, K, V] = PythonExecutor()
    tags: list[str] = field(default_factory=list)
    _initialized: bool = False

    def __post_init__(self):
        self._initialized = True

    def partial(
        self,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> "Task[P, R, K, V]":
        return replace(self, func=functools.partial(self.func, *args, **kwargs))

    def validate(self) -> "Task[P, R, K, V]":
        return replace(
            self,
            func=validate_call(
                self.func,
                validate_return=True,
                config={"arbitrary_types_allowed": True},
            ),
        )

    def __setattr__(self, name, value):
        if self._initialized and name != "_initialized":
            raise FrozenInstanceError(
                "Re-assignment of attributes not permitted post-init. "
                "Use `self.replace` to create a new instance instead."
            )
        return super().__setattr__(name, value)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self.executor.call(self.func, *args, **kwargs)

    def call(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Alias for `self.__call__` for more readable method chaining."""
        return self(*args, **kwargs)

    def map(
        self,
        argnames: str | Sequence[str],
        argvalues: Sequence[V] | Sequence[tuple[V, ...]],
    ) -> Sequence[R]:
        if isinstance(argnames, str):
            argnames = [argnames]
        assert all(
            isinstance(v, type(argvalues[0])) for v in argvalues
        ), "All values in `argvalues` must be of the same type."

        # For mypy, ensure argvalues is a list of tuples, regardless of input
        argvalues_list: list[tuple] = (
            [(v,) for v in argvalues]
            if not isinstance(argvalues[0], tuple)
            else cast(list[tuple], argvalues)
        )
        assert all(
            len(v) == len(argnames) for v in argvalues_list
        ), "All values in `argvalues` must have the same length as `argnames`."
        kwargs_iterable = [
            {argnames[i]: argvalues_list[j][i] for i in range(len(argnames))}
            for j in range(len(argvalues_list))
        ]
        return self.executor.map(lambda kw: self.func(**kw), kwargs_iterable)

    def mapvalues(
        self, argnames: str | Sequence[str], argvalues: Sequence[tuple[K, V]]
    ) -> Sequence[tuple[K, R]]:
        if not isinstance(argnames, str) and len(argnames) > 1:
            raise NotImplementedError(
                "Arg unpacking is not yet supported for `mapvalues`."
            )
        if isinstance(argnames, str):
            argnames = [argnames]
        kwargs_iterable = [(k, {argnames[0]: argvalue}) for (k, argvalue) in argvalues]
        return self.executor.mapvalues(
            lambda kv: (kv[0], self.func(**kv[1])), kwargs_iterable
        )


@overload  # @task style
def task(
    func: Callable[P, R],
    *,
    tags: list[str] | None = None,
) -> Task[P, R, K, V]: ...


@overload  # @task(...) style
def task(
    *,
    tags: list[str] | None = None,
) -> Callable[[Callable[P, R]], Task[P, R, K, V]]: ...


def task(
    func: Callable[P, R] | None = None,
    *,
    tags: list[str] | None = None,
) -> Callable[[Callable[P, R]], Task[P, R, K, V]] | Task[P, R, K, V]:
    def wrapper(
        func: Callable[P, R],
    ) -> Task[P, R, K, V]:
        return Task(
            func,
            tags=tags or [],
        )

    if func:
        return wrapper(func)  # @task style
    return wrapper  # @task(...) style
