from datetime import datetime
from functools import lru_cache
from logging import Logger
from typing import Any

from .exceptions import MSProjectValueSetError


def raise_exception_if_not_datetime(obj) -> None:
    """
    Raise an exception if input is not of required type

    Raises: GitlabSyncError
    """
    if not isinstance(obj, datetime):
        raise MSProjectValueSetError(
            f"The object '{obj}' is of type {type(obj)} but datetime is required"
        )


def convert_to_int_or_raise_exception(value: Any) -> int:
    """
    Convert the give value to int or raise an exception of not possible

    Raises: GitlabSyncError
    """
    try:
        return int(value)
    except (ValueError, TypeError) as e:
        raise MSProjectValueSetError(
            f"Expected a value that can be converted to int, but "
            f"but value '{value}' of type {type(value)} can't be converted: {e}"
        )


@lru_cache(20)
def warn_once(logger: Logger, msg: str):
    logger.warning(msg)
