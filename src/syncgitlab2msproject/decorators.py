import functools
from typing import Callable, Optional, TypeVar

T = TypeVar("T")


def make_none_safe(func: Callable[..., T]) -> Callable[..., Optional[T]]:
    """
    Make sure functions will give None if the first argument is none
    """

    @functools.wraps(func)
    def none_safe(arg, *args, **kwargs):
        if arg is None:
            return None
        else:
            return func(arg, *args, **kwargs)

    return none_safe
