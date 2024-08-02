import re
from typing import Literal, TypeVar

from pydantic import BaseModel, model_serializer


T = TypeVar("T")


class WorkflowVariableBase(BaseModel):
    """Base class for workflow variables."""

    value: str


class EnvVariable(WorkflowVariableBase):
    """A variable that references an environment variable.

    Examples:

    ```python
    >>> parse_variable("${{ env.MY_ENV_VAR }}")
    EnvVariable(value='MY_ENV_VAR')

    ```
    """

    @model_serializer
    def serialize(self) -> str:
        return f'os.environ["{self.value}"]'


class TaskIdVariable(WorkflowVariableBase):
    """A variable that references the return value of another task in the workflow.

    Examples:
    ```python
    >>> parse_variable("${{ workflow.task1.return }}")
    TaskIdVariable(value='task1', suffix='return')

    ```
    """

    suffix: Literal["return"]

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

    pass


SPLIT_SQ_BRACKETS = re.compile(r"(.+)\[(\d+|\*)\]$")


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


def _split_indexed_suffix(s: str) -> tuple[str, str]:
    """Split an indexed suffix into the base suffix and the index.
    If the suffix is not indexed, return a 2-tuple of empty strings.

    Examples:
    ```python
    >>> _split_indexed_suffix("return[0]")
    ('return', '0')
    >>> _split_indexed_suffix("return[1]")
    ('return', '1')
    >>> _split_indexed_suffix("return[*]")
    ('return', '*')
    >>> _split_indexed_suffix("return")
    ('', '')

    ```
    """
    match = re.match(SPLIT_SQ_BRACKETS, s)
    if match:
        parts = match.groups()
        assert len(parts) == 2
        assert all(isinstance(p, str) for p in parts)
        return parts
    else:
        return ("", "")


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
        case ["workflow", task_id, "return"]:
            v = TaskIdVariable(value=task_id, suffix="return")
        case ["workflow", task_id, suffix]:
            match _split_indexed_suffix(suffix):
                case ("return", index) if index.isdigit():
                    v = IndexedTaskIdVariable(
                        value=task_id,
                        suffix="return",
                        tuple_index=index,
                    )
                case ("return", "*"):
                    v = ElementwiseTaskIdVariable(value=task_id, suffix="return")
        case ["env", env_var_name] if (
            _is_valid_env_var_name(env_var_name) and not _is_indexed(env_var_name)
        ):
            return EnvVariable(value=env_var_name)
        case _:
            raise ValueError(
                "Unrecognized variable format. Expected one of: "
                "`${{ workflow.<task_id>.return }}`, "
                "`${{ workflow.<task_id>.return[<tuple_index>] }}`, "
                "`${{ env.<VALID_ENV_VAR_NAME> }}`."
            )
    return v


def _parse_variables(s: str | list[str]) -> str | list[str]:
    if isinstance(s, str):
        return parse_variable(s)
    return [parse_variable(v) for v in s]
