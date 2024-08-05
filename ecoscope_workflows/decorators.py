from dataclasses import FrozenInstanceError, dataclass, field, replace
from typing import Any, Callable, Generic, ParamSpec, TypeVar, overload

from pydantic import validate_call

from ecoscope_workflows.operators import OperatorKws

P = ParamSpec("P")
R = TypeVar("R")


@dataclass
class Task(Generic[P, R]):
    """ """

    func: Callable[P, R]
    validate: bool = False
    operator_kws: OperatorKws = field(default_factory=OperatorKws)
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

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return (
            validate_call(
                self.func,
                validate_return=True,
                config={"arbitrary_types_allowed": True},
            )(*args, **kwargs)
            if self.validate
            else self.func(*args, **kwargs)
        )


@overload  # @task style
def task(
    func: Callable[P, R],
    *,
    image: str | None = None,
    container_resources: dict[str, Any] | None = None,
    tags: list[str] | None = None,
) -> Task[P, R]: ...


@overload  # @task(...) style
def task(
    *,
    image: str | None = None,
    container_resources: dict[str, Any] | None = None,
    tags: list[str] | None = None,
) -> Callable[[Callable[P, R]], Task[P, R]]: ...


def task(
    func: Callable[P, R] | None = None,
    *,
    image: str | None = None,
    container_resources: dict[str, Any] | None = None,
    tags: list[str] | None = None,
) -> Callable[[Callable[P, R]], Task[P, R]] | Task[P, R]:
    operator_kws = {
        k: v
        for k, v in {"image": image, "container_resources": container_resources}.items()
        if v is not None
    }

    def wrapper(
        func: Callable[P, R],
    ) -> Task[P, R]:
        return Task(
            func,
            operator_kws=OperatorKws(**operator_kws),
            tags=tags or [],
        )

    if func:
        return wrapper(func)  # @task style
    return wrapper  # @task(...) style
