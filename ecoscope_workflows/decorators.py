from dataclasses import FrozenInstanceError, dataclass, field, replace
from typing import Callable, Generic, ParamSpec, Sequence, TypeVar, cast, overload

from pydantic import validate_call

from ecoscope_workflows.executors import Executor
from ecoscope_workflows.executors.python import PythonExecutor

P = ParamSpec("P")
R = TypeVar("R")
K = TypeVar("K")
V = TypeVar("V")


@dataclass
class Task(Generic[P, R, K, V]):
    """ """

    func: Callable[P, R]
    validate: bool = False
    executor: Executor[P, R, K, V] = PythonExecutor()
    tags: list[str] = field(default_factory=list)
    _initialized: bool = False

    def __post_init__(self):
        self._initialized = True

    def replace(
        self,
        validate: bool | None = None,
    ) -> "Task[P, R, K, V]":
        self._initialized = False
        changes = {
            k: v
            for k, v in {
                "validate": validate,
            }.items()
            if v is not None
        }
        return replace(self, **changes)  # type: ignore

    def __setattr__(self, name, value):
        if self._initialized and name != "_initialized":
            raise FrozenInstanceError(
                "Re-assignment of attributes not permitted post-init. "
                "Use `self.replace` to create a new instance instead."
            )
        return super().__setattr__(name, value)

    @property
    def _callable(self) -> Callable[P, R]:
        return (
            validate_call(
                self.func,
                validate_return=True,
                config={"arbitrary_types_allowed": True},
            )
            if self.validate
            else self.func
        )

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self.executor.call(self._callable, *args, **kwargs)

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
        return self.executor.map(lambda kw: self._callable(**kw), kwargs_iterable)

    def mapvalues(
        self, argname: str, argvalues: Sequence[tuple[K, V]]
    ) -> Sequence[tuple[K, R]]:
        # TODO: argname unpacking like in `map`
        kwargs_iterable = [(k, {argname: argvalue}) for (k, argvalue) in argvalues]
        return self.executor.mapvalues(
            lambda kv: (kv[0], self._callable(**kv[1])), kwargs_iterable
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
