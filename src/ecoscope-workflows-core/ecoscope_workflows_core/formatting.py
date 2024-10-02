import functools
import subprocess
import sys
from typing import Callable


def ruff_formatted(returns_str_func: Callable[..., str]) -> Callable:
    """Decorator to format the output of a function that returns a string with ruff."""

    @functools.wraps(returns_str_func)
    def wrapper(*args, **kwargs):
        unformatted = returns_str_func(*args, **kwargs)
        # https://github.com/astral-sh/ruff/issues/8401#issuecomment-1788806462
        formatted = subprocess.check_output(
            [sys.executable, "-m", "ruff", "format", "-s", "-"],
            input=unformatted,
            encoding="utf-8",
        )
        linted = subprocess.check_output(
            [sys.executable, "-m", "ruff", "check", "--fix", "--exit-zero", "-s", "-"],
            input=formatted,
            encoding="utf-8",
        )
        return linted

    return wrapper
