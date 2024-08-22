import functools
import inspect
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import (
    Any,
    Callable,
    Generic,
    Literal,
    ParamSpec,
    Sequence,
    TypeVar,
    cast,
    overload,
)

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from pydantic import validate_call

from ecoscope_workflows.executors import (
    AsyncExecutor,
    Future,
    FutureSequence,
    SyncExecutor,
    mapvalues_wrapper,
)
from ecoscope_workflows.executors.python import PythonExecutor

P = ParamSpec("P")
R = TypeVar("R")
K = TypeVar("K")
V = TypeVar("V")


@dataclass(frozen=True)
class _Task(Generic[P, R, K, V]):
    func: Callable[P, R]
    tags: list[str]

    def partial(
        self,
        **kwargs: dict,
    ) -> Self:
        """Return a new Task with the same attributes, but with the function converted
        into a partial function with the given keyword arguments. This is useful for
        mapping a function over an iterable where some of the function's arguments are
        constant across all calls.

        Examples:

        ```python
        >>> @task
        ... def f(a: int, b: int) -> int:
        ...     return a + b
        >>> f.partial(a=1).call(b=2)
        3
        >>> f.partial(a=1).map("b", [2, 3])
        [3, 4]
        >>> f.partial(a=1).mapvalues("b", [("x", 2), ("y", 3)])
        [('x', 3), ('y', 4)]

        ```

        """
        return replace(self, func=functools.partial(self.func, **kwargs))

    def validate(self) -> Self:
        """Return a new Task with the same attributes, but with the function input
        parameters and return values validated by Pydantic's `validate_call` This
        is required in settings where the input parameters are given as strings that
        need to be parsed into the correct Python type before being passed to the task
        function, such as calling workflows as scripts with parameters provided in text
        config files, or when calling workflows over http with parameters provided as json
        in the http request body.

        Examples:

        ```python
        >>> @task
        ... def f(a: int) -> int:
        ...     return a
        >>> f("1")  # no parsing without validate; input value is returned as a string
        '1'
        >>> f("2")
        '2'
        >>> f.validate().call("1")  # with validate, input value is parsed into an int
        1
        >>> f.validate().call("2")
        2

        ```

        """
        return replace(
            self,
            func=validate_call(
                self.func,
                validate_return=True,
                config={"arbitrary_types_allowed": True},
            ),
        )

    @overload
    def set_executor(
        self,
        name_or_executor: Literal["python"],
    ) -> "SyncTask[P, R, K, V]": ...

    @overload
    def set_executor(
        self,
        name_or_executor: Literal["lithops"],
    ) -> "AsyncTask[P, R, K, V]": ...

    @overload
    def set_executor(
        self,
        name_or_executor: SyncExecutor,
    ) -> "SyncTask[P, R, K, V]": ...

    @overload
    def set_executor(
        self,
        name_or_executor: AsyncExecutor,
    ) -> "AsyncTask[P, R, K, V]": ...

    def set_executor(
        self,
        name_or_executor: Literal["python", "lithops"] | AsyncExecutor | SyncExecutor,
    ) -> "AsyncTask[P, R, K, V] | SyncTask[P, R, K, V]":
        """Return a new Task with the same attributes, but with the executor set to the
        given executor. This is useful for changing the executor for a task function
        after it has been defined.

        Examples:

        ```python
        >>> @task
        ... def f(a: int, b: int) -> int:
        ...     return a + b
        >>> type(f.executor)
        <class 'ecoscope_workflows.executors.python.PythonExecutor'>
        >>> f_new = f.set_executor("lithops")
        >>> type(f_new.executor)
        <class 'ecoscope_workflows.executors.lithops.LithopsExecutor'>

        ```

        """
        match name_or_executor:
            case "python":
                return SyncTask(
                    self.func,
                    tags=self.tags,
                    executor=PythonExecutor(),
                )
            case "lithops":
                from ecoscope_workflows.executors.lithops import LithopsExecutor

                return AsyncTask(
                    self.func,
                    tags=self.tags,
                    executor=LithopsExecutor(),
                )
            case AsyncExecutor():
                return AsyncTask(
                    self.func,
                    tags=self.tags,
                    executor=name_or_executor,
                )
            case SyncExecutor():
                return SyncTask(
                    self.func,
                    tags=self.tags,
                    executor=name_or_executor,
                )
            case _:
                raise ValueError(
                    "Executor name must be one of the literal strings 'python' or 'lithops', "
                    f"or an instance of a `AsyncExecutor` or `SyncExecutor`, not {name_or_executor}."
                )


class TaskMethodsMixinABC(ABC, Generic[P, R, K, V]):
    @abstractmethod
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R | Future[R]: ...

    @abstractmethod
    def call(self, *args: P.args, **kwargs: P.kwargs) -> R | Future[R]: ...

    @abstractmethod
    def map(
        self,
        argnames: str | Sequence[str],
        argvalues: Sequence[V] | Sequence[tuple[V, ...]],
    ) -> Sequence[R] | FutureSequence[R]: ...

    @abstractmethod
    def mapvalues(
        self, argnames: str | Sequence[str], argvalues: Sequence[tuple[K, V]]
    ) -> Sequence[tuple[K, R]] | FutureSequence[tuple[K, R]]: ...


def _get_defaults(func: Callable) -> dict[str, Any]:
    return {
        k: v.default
        for k, v in inspect.signature(func).parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def _create_kwargs_iterable(
    argnames: str | Sequence[str],
    argvalues: Sequence[V] | Sequence[tuple[V, ...]],
    defaults: dict[str, Any],
) -> list[dict[str, V | Any]]:
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
    return [
        defaults | {argnames[i]: argvalues_list[j][i] for i in range(len(argnames))}
        for j in range(len(argvalues_list))
    ]


def _wrap_for_mapvalues(func: Callable[P, R]) -> Callable[[tuple[K, V]], tuple[K, R]]:
    wrapper: mapvalues_wrapper = mapvalues_wrapper(func)
    functools.update_wrapper(wrapper, func)
    return wrapper


@dataclass(frozen=True)
class SyncTask(TaskMethodsMixinABC, _Task[P, R, K, V]):
    """The implementation of `@task`. This class is used to wrap a task function
    and provide methods for calling the task function, mapping it over an iterable
    of arguments, and mapping it over an iterable of key-value pairs. Any of these
    methods can be chained with the `partial` method to set some of the task function's
    arguments before calling or mapping. Any of these methods can also be chained with
    the `validate` method to parse the task function's input parameters and return
    values using Pydantic's `validate_call` wrapper. The task function is executed
    using an `Executor` instance, which can be set to a specific executor using the
    `executor` attribute, or left as the default `PythonExecutor`.

    Examples:

    ```python
    >>> @task
    ... def f(a: int, b: int) -> int:
    ...     return a + b
    >>> f(1, 2)
    3
    >>> f.call(1, 2)
    3
    >>> f.partial(a=1)(b=2)
    3
    >>> f.partial(a=1).call(b=2)
    3
    >>> f.partial(a=1).map("b", [2, 3])
    [3, 4]
    >>> f.partial(a=1).mapvalues("b", [("x", 2), ("y", 3)])
    [('x', 3), ('y', 4)]
    >>> f.validate().call("1", "2")  # coerce input values to ints
    3
    >>> f.validate().partial(a="1").map("b", ["2", "3"])  # type coercion with map
    [3, 4]
    >>> f.validate().partial(a="1").mapvalues("b", [("x", "2"), ("y", "3")])
    [('x', 3), ('y', 4)]

    ```

    """

    executor: SyncExecutor = field(default_factory=PythonExecutor)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self.executor.call(self.func, *args, **kwargs)

    def call(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Alias for `self.__call__` for more readable method chaining.

        Examples:

        ```python
        >>> @task
        ... def f(a: int, b: int) -> int:
        ...     return a + b
        >>> f(1, 2)
        3
        >>> f.call(1, 2)
        3
        >>> f.partial(a=1)(b=2)  # this works but is less readable
        3
        >>> f.partial(a=1).call(b=2)  # this is more readable
        3

        ```

        """
        return self(*args, **kwargs)

    def map(
        self,
        argnames: str | Sequence[str],
        argvalues: Sequence[V] | Sequence[tuple[V, ...]],
    ) -> Sequence[R]:
        """Map the task function over an iterable of argvalues where each element of the
        argvalues is either a single value or a tuple of values that correspond to the
        argnames. If the argvalues are single values, argnames must be a single string,
        or a sequence of length 1. If the argvalues are tuples, the length of each tuple
        must match the length of the sequence of argnames. To statically set one or more
        arguments before mapping, chain with the `partial` method.

        Examples:

        ```python
        >>> @task
        ... def f(a: int) -> int:
        ...     return a
        >>> f.map("a", [1, 2, 3])  # single argument
        [1, 2, 3]
        >>> @task
        ... def g(a: int, b: int) -> int:
        ...     return a + b
        >>> g.map(["a", "b"], [(1, 2), (3, 4), (5, 6)])  # multiple arguments
        [3, 7, 11]
        >>> g.partial(a=1).map("b", [2, 3, 4])  # statically set one argument
        [3, 4, 5]
        >>> @task
        ... def h(a: int, b: int, c: int) -> int:
        ...     return a + b + c
        >>> h.partial(a=1, b=2).map("c", [3, 4, 5])  # statically set multiple arguments
        [6, 7, 8]

        ```
        """
        defaults = _get_defaults(self.func)
        kwargs_iterable = _create_kwargs_iterable(argnames, argvalues, defaults)
        return self.executor.map(lambda kw: self.func(**kw), kwargs_iterable)

    def mapvalues(
        self, argnames: str | Sequence[str], argvalues: Sequence[tuple[K, V]]
    ) -> Sequence[tuple[K, R]]:
        """Map the task function over an iterable of key-value pairs, applying the
        task function to the values while keeping the keys unchanged. The argvalues
        must be a sequence of tuples where the first element of each tuple is the
        key to passthrough, and the second element is the value to transform.
        The argnames must be a single string, or a sequence of length 1, that
        corresponds to the name of the value in the task function signature.
        Compare to `pyspark.RDD.mapValues`: https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.RDD.mapValues.html.

        To statically set one or more arguments before mapping values, chain with `partial`.

        Examples:

        ```python
        >>> @task
        ... def f(x: str) -> int:
        ...     return len(x)
        >>> f.mapvalues("x", [("a", ["apple", "banana", "lemon"]), ("b", ["grapes"])])
        [('a', 3), ('b', 1)]
        >>> @task
        ... def g(x: str, y: int) -> int:
        ...     return len(x) * y
        >>> g.partial(y=2).mapvalues("x", [("a", "apple"), ("b", "banana")])
        [('a', 10), ('b', 12)]

        ```

        """
        if not isinstance(argnames, str) and len(argnames) > 1:
            raise NotImplementedError(
                "Arg unpacking is not yet supported for `mapvalues`."
            )
        if isinstance(argnames, str):
            argnames = [argnames]
        defaults = _get_defaults(self.func)
        kwargs_iterable = [
            (k, defaults | {argnames[0]: argvalue}) for (k, argvalue) in argvalues
        ]
        return self.executor.map(_wrap_for_mapvalues(self.func), kwargs_iterable)


@dataclass(frozen=True)
class AsyncTask(TaskMethodsMixinABC, _Task[P, R, K, V]):
    executor: AsyncExecutor

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Future[R]:
        return self.executor.call(self.func, *args, **kwargs)

    def call(self, *args: P.args, **kwargs: P.kwargs) -> Future[R]:
        return self(*args, **kwargs)

    def map(
        self,
        argnames: str | Sequence[str],
        argvalues: Sequence[V] | Sequence[tuple[V, ...]],
    ) -> FutureSequence[R]:
        defaults = _get_defaults(self.func)
        kwargs_iterable = _create_kwargs_iterable(argnames, argvalues, defaults)
        return self.executor.map(self.func, kwargs_iterable)

    def mapvalues(
        self, argnames: str | Sequence[str], argvalues: Sequence[tuple[K, V]]
    ) -> FutureSequence[tuple[K, R]]:
        if not isinstance(argnames, str) and len(argnames) > 1:
            raise NotImplementedError(
                "Arg unpacking is not yet supported for `mapvalues`."
            )
        if isinstance(argnames, str):
            argnames = [argnames]
        defaults = _get_defaults(self.func)
        kwargs_iterable = [
            (k, defaults | {argnames[0]: argvalue}) for (k, argvalue) in argvalues
        ]
        return self.executor.map(_wrap_for_mapvalues(self.func), kwargs_iterable)


@overload  # @task style
def task(
    func: Callable[P, R],
    *,
    tags: list[str] | None = None,
) -> SyncTask[P, R, K, V]: ...


@overload  # @task(...) style
def task(
    *,
    tags: list[str] | None = None,
) -> Callable[[Callable[P, R]], SyncTask[P, R, K, V]]: ...


def task(
    func: Callable[P, R] | None = None,
    *,
    tags: list[str] | None = None,
) -> Callable[[Callable[P, R]], SyncTask[P, R, K, V]] | SyncTask[P, R, K, V]:
    def wrapper(
        func: Callable[P, R],
    ) -> SyncTask[P, R, K, V]:
        return SyncTask(
            func,
            tags=tags or [],
        )

    if func:
        return wrapper(func)  # @task style
    return wrapper  # @task(...) style


Task = AsyncTask | SyncTask
