import functools
import types
import warnings
from dataclasses import FrozenInstanceError, dataclass, field, replace
from typing import Any, Callable, Generic, TypeVar, overload

import dill
from pydantic import validate_call
from pydantic.functional_validators import AfterValidator, BeforeValidator

from ecoscope_workflows.operators import OperatorKws

FuncReturn = TypeVar("FuncReturn")
ReturnPostValidatorReturn = TypeVar("ReturnPostValidatorReturn")


def _get_annotation_metadata(func: types.FunctionType, arg_name: str):
    assert func.__annotations__, f"{func.__name__=} has no annotations."
    assert (
        arg_name in func.__annotations__
    ), f"{arg_name=} on {func.__name__=} is not annotated."
    assert hasattr(
        func.__annotations__[arg_name], "__metadata__"
    ), f"The annotation of {arg_name=} on {func.__name__=} is not of type `typing.Annotated`."
    return list(func.__annotations__[arg_name].__metadata__)


def _get_validator_index(
    existing_meta: dict,
    validator_type: AfterValidator | BeforeValidator,
) -> int:
    """If there are is an existing validator instance of the specified type in the metadata,
    we will overwrite it by re-assigning to its index. if not, we will just add our new
    validator to the end of the list (i.e., index it as -1)
    """
    return (
        -1
        if not any([isinstance(m, validator_type) for m in existing_meta])
        else [i for i, m in enumerate(existing_meta) if isinstance(m, validator_type)][
            0
        ]
    )


@dataclass
class DistributedTask(Generic[FuncReturn, ReturnPostValidatorReturn]):
    """
    Parameters
    ----------
    func : Callable
        The function (or other callable) to wrap.
    arg_prevalidators : dict[ArgName, Callable]
        ...
    """

    func: Callable[..., FuncReturn]
    arg_prevalidators: dict[str, Callable[[str], Any]] = field(default_factory=dict)
    return_postvalidator: Callable[..., ReturnPostValidatorReturn] | None = None
    validate: bool = False
    operator_kws: OperatorKws = field(default_factory=OperatorKws)
    tags: list[str] = field(default_factory=list)
    _initialized: bool = False

    def __post_init__(self):
        functools.update_wrapper(self, self.func)
        self._initialized = True

    def replace(
        self,
        arg_prevalidators: dict[str, Callable] | None = None,
        return_postvalidator: Callable | None = None,
        validate: bool | None = None,
    ) -> "DistributedTask[FuncReturn, ReturnPostValidatorReturn]":
        self._initialized = False
        changes = {
            k: v
            for k, v in {
                "arg_prevalidators": arg_prevalidators,
                "return_postvalidator": return_postvalidator,
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

    def __call__(self, *args, **kwargs) -> FuncReturn | ReturnPostValidatorReturn:
        # to get distributed behaviors, we need to mutate the __annotations__ dict of
        # the function before calling it. if we don't make a deep copy, these changes
        # will effect future calls. this is a way to make a copy that doesn't share a
        # reference to the original __annotations__ dict. perhaps a function factory
        # would be a more robust approach.
        func_copy = dill.loads(dill.dumps(self.func))
        # TODO: make sure the keys of arg_prevalidators are all arg_names on self.func
        for arg_name in self.arg_prevalidators:
            arg_meta = _get_annotation_metadata(func_copy, arg_name)
            bv_idx = _get_validator_index(arg_meta, validator_type=BeforeValidator)
            arg_meta[bv_idx] = BeforeValidator(func=self.arg_prevalidators[arg_name])
            func_copy.__annotations__[arg_name].__metadata__ = tuple(arg_meta)
        # TODO: make sure return_postvalidator is a single-argument callable
        if self.return_postvalidator:
            return_meta = _get_annotation_metadata(func_copy, "return")
            av_idx = _get_validator_index(return_meta, validator_type=AfterValidator)
            return_meta[av_idx] = AfterValidator(func=self.return_postvalidator)
            func_copy.__annotations__["return"].__metadata__ = tuple(return_meta)
        # TODO: If `ecoscope.distributed.types.DataFrame` is used as an arg or return type,
        # and it is *not* subscripted with a pandera schema, we get a cryptic error from
        # pydantic under validate=True contexts... make this error more descriptive or catch
        # it somewhere in this decorator before making this call and confusing everyone.
        if (self.arg_prevalidators or self.return_postvalidator) and not self.validate:
            warnings.warn(
                f"`@distributed`-decorated function has `{self.arg_prevalidators=}` "
                f"and  `{self.return_postvalidator=}` but `{self.validate=}`. Pre- "
                "and post- call behavior is only modified when `self.validate=True`."
            )
        return (
            validate_call(
                func_copy,
                validate_return=True,
                config={"arbitrary_types_allowed": True},
            )(*args, **kwargs)
            if self.validate
            else func_copy(*args, **kwargs)
        )


@overload  # @distributed style
def distributed(
    func: Callable[..., FuncReturn],
    *,
    image: str | None = None,
    container_resources: dict[str, Any] | None = None,
    tags: list[str] | None = None,
) -> DistributedTask[FuncReturn, ReturnPostValidatorReturn]: ...


@overload  # @distributed(...) style
def distributed(
    *,
    image: str | None = None,
    container_resources: dict[str, Any] | None = None,
    tags: list[str] | None = None,
) -> Callable[
    [Callable[..., FuncReturn]],
    DistributedTask[FuncReturn, ReturnPostValidatorReturn],
]: ...


def distributed(
    func: Callable[..., FuncReturn] | None = None,
    *,
    image: str | None = None,
    container_resources: dict[str, Any] | None = None,
    tags: list[str] | None = None,
) -> (
    Callable[..., DistributedTask[FuncReturn, ReturnPostValidatorReturn]]
    | DistributedTask[FuncReturn, ReturnPostValidatorReturn]
):
    operator_kws = {
        k: v
        for k, v in {"image": image, "container_resources": container_resources}.items()
        if v is not None
    }

    def wrapper(
        func: Callable[..., FuncReturn],
    ) -> DistributedTask[FuncReturn, ReturnPostValidatorReturn]:
        return DistributedTask(
            func,
            operator_kws=OperatorKws(**operator_kws),
            tags=tags or [],
        )

    if func:
        return wrapper(func)  # @distributed style
    return wrapper  # @distributed(...) style
