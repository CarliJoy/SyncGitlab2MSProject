# -*- coding: utf-8 -*-

import pytest
from syncgitlab2msproject.cli import fib

__author__ = "Carli"
__copyright__ = "Carli"
__license__ = "mit"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
