from dataclasses import FrozenInstanceError, dataclass, field, replace
from typing import Any, Callable, Generic, ParamSpec, TypeVar, overload

from pydantic import validate_call

from ecoscope_workflows.operators import OperatorKws

P = ParamSpec("P")
R = TypeVar("R")


@dataclass
class DistributedTask(Generic[P, R]):
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
    ) -> "DistributedTask[P, R]":
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
            validate_call(self.func)(*args, **kwargs)
            if self.validate
            else self.func(*args, **kwargs)
        )


@overload  # @distributed style
def distributed(
    func: Callable[P, R],
    *,
    image: str | None = None,
    container_resources: dict[str, Any] | None = None,
    tags: list[str] | None = None,
) -> DistributedTask[P, R]: ...


@overload  # @distributed(...) style
def distributed(
    *,
    image: str | None = None,
    container_resources: dict[str, Any] | None = None,
    tags: list[str] | None = None,
) -> Callable[[Callable[P, R]], DistributedTask[P, R]]: ...


def distributed(
    func: Callable[P, R] | None = None,
    *,
    image: str | None = None,
    container_resources: dict[str, Any] | None = None,
    tags: list[str] | None = None,
) -> Callable[[Callable[P, R]], DistributedTask[P, R]] | DistributedTask[P, R]:
    operator_kws = {
        k: v
        for k, v in {"image": image, "container_resources": container_resources}.items()
        if v is not None
    }

    def wrapper(
        func: Callable[P, R],
    ) -> DistributedTask[P, R]:
        return DistributedTask(
            func,
            operator_kws=OperatorKws(**operator_kws),
            tags=tags or [],
        )

    if func:
        return wrapper(func)  # @distributed style
    return wrapper  # @distributed(...) style
