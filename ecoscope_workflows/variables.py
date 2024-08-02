import re
from abc import ABC, abstractmethod
from typing import Literal, TypeVar, cast

from pydantic import BaseModel, model_serializer


T = TypeVar("T")


class WorkflowVariableABC(ABC, BaseModel):
    """Base class for workflow variables."""

    value: str

    @abstractmethod
    def is_iterable(self) -> bool:
        raise NotImplementedError


class EnvVariable(WorkflowVariableABC):
    """A variable that references an environment variable.

    Examples:

    ```python
    >>> parse_variable("${{ env.MY_ENV_VAR }}")
    EnvVariable(value='MY_ENV_VAR')

    ```
    """

    def is_iterable(self) -> Literal[False]:
        return False

    @model_serializer
    def serialize(self) -> str:
        return f'os.environ["{self.value}"]'


class TaskIdVariable(WorkflowVariableABC):
    """A variable that references the return value of another task in the workflow.

    Examples:
    ```python
    >>> parse_variable("${{ workflow.task1.return }}")
    TaskIdVariable(value='task1', suffix='return')

    ```
    """

    suffix: Literal["return"]

    def is_iterable(self) -> bool:
        return False

    @model_serializer
    def serialize(self) -> str:
        return self.value


class IndexedTaskIdVariable(TaskIdVariable):
    """A variable that references the return value of another task in the workflow,
    for which the return value is a tuple, and indexes to a specific value in the tuple.

    Examples:
    ```python
    >>> parse_variable("${{ workflow.task1.return[0] }}")
    IndexedTaskIdVariable(value='task1', suffix='return', tuple_index=0)
    >>> parse_variable("${{ workflow.task1.return[1] }}")
    IndexedTaskIdVariable(value='task1', suffix='return', tuple_index=1)

    ```
    """

    tuple_index: int

    def is_iterable(self) -> Literal[False]:
        return False


class ElementwiseTaskIdVariable(TaskIdVariable):
    """A variable that references the return value of another task in the workflow,
    for which the return value is a list, and indexes elementwise into that list.

    Examples:
    ```python
    >>> parse_variable("${{ workflow.task1.return[*] }}")
    ElementwiseTaskIdVariable(value='task1', suffix='return')
    >>> parse_variable("${{ workflow.task1.return[*] }}")
    ElementwiseTaskIdVariable(value='task1', suffix='return')

    ```
    """

    def is_iterable(self) -> Literal[True]:
        return True


SPLIT_SQ_BRACKETS = re.compile(r"(.+?)\[(\d+|\*)\](?:\[(\d+|\*)\])?")


def _is_indexed(s: str) -> bool:
    """Check if a string is indexed, e.g. `return[0]`.

    Examples:
    ```python
    >>> _is_indexed("return[0]")
    True
    >>> _is_indexed("return[1]")
    True
    >>> _is_indexed("return")
    False

    ```
    """
    return bool(re.match(SPLIT_SQ_BRACKETS, s))


def _is_valid_env_var_name(name: str) -> bool:
    """Check if a string is a valid environment variable name.

    Examples:
    ```python
    >>> _is_valid_env_var_name("MY_ENV_VAR")
    True
    >>> _is_valid_env_var_name("MY_ENV_VAR_1")
    True
    >>> _is_valid_env_var_name("1_MY_ENV_VAR")
    False

    ```
    """

    return bool(re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name))


SplitSuffix = tuple[str, str | None, str | None]


def _split_suffix(s: str) -> SplitSuffix:
    """Split an indexed or unindexed suffix into the base suffix and the index(es).

    Examples:
    ```python
    >>> _split_suffix("return")
    ('return', None, None)
    >>> _split_suffix("return[0]")
    ('return', '0', None)
    >>> _split_suffix("return[1]")
    ('return', '1', None)
    >>> _split_suffix("return[*]")
    ('return', '*', None)
    >>> _split_suffix("return[*][*]")
    ('return', '*', '*')
    >>> _split_suffix("return[*][0]")
    ('return', '*', '0')
    >>> _split_suffix("return[*][1]")
    ('return', '*', '1')


    ```
    """
    match = re.match(SPLIT_SQ_BRACKETS, s)
    return cast(SplitSuffix, match.groups()) if match else ("return", None, None)


def _parse_task_id_variable(
    task_id: str,
    suffix: str,
) -> TaskIdVariable | IndexedTaskIdVariable | ElementwiseTaskIdVariable:
    match _split_suffix(suffix):
        case ("return", None, None):
            return TaskIdVariable(value=task_id, suffix="return")
        case ("return", str(index), None) if index.isdigit():
            return IndexedTaskIdVariable(
                value=task_id,
                suffix="return",
                tuple_index=index,
            )
        case ("return", "*", None):
            return ElementwiseTaskIdVariable(value=task_id, suffix="return")
        case ("return", "*", str(index)) if index.isdigit():
            raise NotImplementedError
        case ("return", "*", "*"):
            raise NotImplementedError
        case (
            "return",
            str(index),
            str(index2),
        ) if index.isdigit() and index2.isdigit():
            raise NotImplementedError
        case ("return", str(index), "*") if index.isdigit():
            raise NotImplementedError
        case _:
            raise ValueError(
                "Unrecognized task id variable format. Expected one of: "
                "`${{ workflow.<task_id>.return }}`, "
                "`${{ workflow.<task_id>.return[<index>] }}`, "
                "`${{ workflow.<task_id>.return[<index>][<index>] }}`. "
                "Where index is a non-negative integer or `*`."
            )


def parse_variable(s: str) -> TaskIdVariable | IndexedTaskIdVariable | EnvVariable:
    """Parse a variable reference from a string into a `TaskIdVariable` or `EnvVariable`.

    Examples:

    ```python
    >>> parse_variable("${{ workflow.task1.return }}")
    TaskIdVariable(value='task1', suffix='return')
    >>> parse_variable("${{ workflow.task1.return[0] }}")
    IndexedTaskIdVariable(value='task1', suffix='return', tuple_index=0)
    >>> parse_variable("${{ workflow.task1.return[1] }}")
    IndexedTaskIdVariable(value='task1', suffix='return', tuple_index=1)
    >>> parse_variable("${{ env.MY_ENV_VAR }}")
    EnvVariable(value='MY_ENV_VAR')

    ```
    """
    if not (s.startswith("${{") and s.endswith("}}")):
        raise ValueError(
            f"`{s}` is not a valid variable. " "Variables must be wrapped in `${{ }}`."
        )
    inner = s.replace("${{", "").replace("}}", "").strip()
    match inner.split("."):
        case ["workflow", task_id, suffix]:
            return _parse_task_id_variable(task_id, suffix)
        case ["env", env_var_name] if (
            _is_valid_env_var_name(env_var_name) and not _is_indexed(env_var_name)
        ):
            return EnvVariable(value=env_var_name)
        case _:
            raise ValueError(
                "Unrecognized variable format. Expected one of: "
                "`${{ workflow.<task_id>.<suffix> }}`, "
                "`${{ env.<VALID_ENV_VAR_NAME> }}`."
            )


def _parse_variables(s: str | list[str]) -> str | list[str]:
    if isinstance(s, str):
        return parse_variable(s)
    return [parse_variable(v) for v in s]
