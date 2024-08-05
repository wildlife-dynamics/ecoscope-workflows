from dataclasses import FrozenInstanceError, dataclass, field, replace
from typing import Callable, Generic, ParamSpec, Sequence, TypeVar, overload

from pydantic import validate_call

from ecoscope_workflows.executors import Executor
from ecoscope_workflows.executors.python import PythonExecutor

P = ParamSpec("P")
R = TypeVar("R")


@dataclass
class Task(Generic[P, R]):
    """ """

    func: Callable[P, R]
    validate: bool = False
    executor: Executor[P, R] = PythonExecutor()
    tags: list[str] = field(default_factory=list)
    _initialized: bool = False

    def __post_init__(self):
        self._initialized = True

    def replace(
        self,
        validate: bool | None = None,
    ) -> "Task[P, R]":
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

    def map(self, iterable: Sequence) -> Sequence[R]:
        return self.executor.map(self._callable, iterable)


@overload  # @task style
def task(
    func: Callable[P, R],
    *,
    tags: list[str] | None = None,
) -> Task[P, R]: ...


@overload  # @task(...) style
def task(
    *,
    tags: list[str] | None = None,
) -> Callable[[Callable[P, R]], Task[P, R]]: ...


def task(
    func: Callable[P, R] | None = None,
    *,
    tags: list[str] | None = None,
) -> Callable[[Callable[P, R]], Task[P, R]] | Task[P, R]:
    def wrapper(
        func: Callable[P, R],
    ) -> Task[P, R]:
        return Task(
            func,
            tags=tags or [],
        )

    if func:
        return wrapper(func)  # @task style
    return wrapper  # @task(...) style
