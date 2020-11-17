import functools
from typing import Callable, Optional, TypeVar

T_IN = TypeVar("T_IN")
T_OUT = TypeVar("T_OUT")

"""
Overload variants to show that the value is only None if None was given

Note: This overloading is readable but not recognized by mypy, so we drop it for
      the moment but still keep it

@overload
def make_none_safe(func: Callable[[T_IN], T_OUT]) -> Callable[[T_IN], T_OUT]: ...

@overload
def make_none_safe(func: Callable[[None], None]) -> Callable[[None], None]: ...
"""


def make_none_safe(
    func: Callable[[T_IN], T_OUT]
) -> Callable[[Optional[T_IN]], Optional[T_OUT]]:
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
