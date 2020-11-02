import functools
from typing import Callable, Any, Optional


def make_none_safe(func: Callable[..., Any]) -> Callable[..., Optional[Any]]:
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
