# -*- coding: utf-8 -*-
from typing import Any, Union

import pytest
from syncgitlab2msproject.ms_project import MSProject
from pathlib import Path
from inspect import getattr_static, signature
from datetime import datetime

__author__ = "Carli"
__copyright__ = "Carli"
__license__ = "mit"


BASE_DIR = Path(__file__).absolute().parent
TEST_FILE = BASE_DIR / "Project1.mpp"


class DoNotSave(Exception):
    pass


def get_prop_set_type_annotation(obj: Any, property_name: str) -> Union[str, type]:
    """
    Get the type annotation of obj for property
    """

    # Combination of
    # https://stackoverflow.com/a/9917213/3813064 and
    # https://stackoverflow.com/questions/53949473/python-dynamically-access-type-annotation-of-a-property
    sign = signature(getattr_static(obj, property_name).fset)
    return next(reversed(sign.parameters.values())).annotation


def test_printing_all():
    assert TEST_FILE.is_file()
    print(f"Loading '{TEST_FILE}'")
    with pytest.raises(DoNotSave):
        with MSProject(TEST_FILE) as tasks:
            # Test defined Number of Tasks
            assert len(tasks) == 17
            # Test cycling through all tasks
            for i, task in enumerate(tasks):
                if task:
                    print(f"*{i:>4}: '{task.name}'")
                else:
                    print(f"#{i:>4}  >is empty<")
            # Test printing all
            for attribute in dir(tasks[0]):
                if not attribute.startswith("_"):
                    print(f"{attribute} = {getattr(tasks[0], attribute)}")
            for attribute in dir(tasks[0]):
                if not attribute.startswith("_"):
                    print(attribute)
                    prop_type = get_prop_set_type_annotation(tasks[0], attribute)
                    print(prop_type)
                    if prop_type == datetime:
                        pass
            raise DoNotSave("We do not want the file to save!")