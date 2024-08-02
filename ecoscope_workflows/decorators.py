import functools
from dataclasses import FrozenInstanceError, dataclass, field, replace
from typing import Any, Callable, Generic, TypeVar, overload

from pydantic import validate_call

from ecoscope_workflows.operators import OperatorKws

FuncReturn = TypeVar("FuncReturn")


@dataclass
class DistributedTask(Generic[FuncReturn]):
    """ """

    func: Callable[..., FuncReturn]
    validate: bool = False
    operator_kws: OperatorKws = field(default_factory=OperatorKws)
    tags: list[str] = field(default_factory=list)
    _initialized: bool = False

    def __post_init__(self):
        functools.update_wrapper(self, self.func)
        self._initialized = True

    def replace(
        self,
        validate: bool | None = None,
    ) -> "DistributedTask[FuncReturn]":
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

    def __call__(self, *args, **kwargs) -> FuncReturn:
        return (
            validate_call(self.func, validate_return=True)(*args, **kwargs)
            if self.validate
            else self.func(*args, **kwargs)
        )


@overload  # @distributed style
def distributed(
    func: Callable[..., FuncReturn],
    *,
    image: str | None = None,
    container_resources: dict[str, Any] | None = None,
    tags: list[str] | None = None,
) -> DistributedTask[FuncReturn]: ...


@overload  # @distributed(...) style
def distributed(
    *,
    image: str | None = None,
    container_resources: dict[str, Any] | None = None,
    tags: list[str] | None = None,
) -> Callable[
    [Callable[..., FuncReturn]],
    DistributedTask[FuncReturn],
]: ...


def distributed(
    func: Callable[..., FuncReturn] | None = None,
    *,
    image: str | None = None,
    container_resources: dict[str, Any] | None = None,
    tags: list[str] | None = None,
) -> Callable[..., DistributedTask[FuncReturn]] | DistributedTask[FuncReturn]:
    operator_kws = {
        k: v
        for k, v in {"image": image, "container_resources": container_resources}.items()
        if v is not None
    }

    def wrapper(
        func: Callable[..., FuncReturn],
    ) -> DistributedTask[FuncReturn]:
        return DistributedTask(
            func,
            operator_kws=OperatorKws(**operator_kws),
            tags=tags or [],
        )

    if func:
        return wrapper(func)  # @distributed style
    return wrapper  # @distributed(...) style
