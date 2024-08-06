import functools
from dataclasses import dataclass, field, replace
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

    def partial(
        self,
        **kwargs: dict,
    ) -> "Task[P, R, K, V]":
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

    def validate(self) -> "Task[P, R, K, V]":
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
