# -*- coding: utf-8 -*-
from typing import Any, Union, Optional

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

    def check_setting_val(obj: Any, attrib: str, prop_type: Union[type, None]):
        if prop_type == datetime:
            new_value = datetime(2020, 3, 4, 20, 15, 30).astimezone()
        elif prop_type == int:
            new_value = 5
        elif prop_type == str:
            new_value = "Test String"
        elif prop_type == bool:
            new_value = True
        elif prop_type is None:
            new_value = None
        else:
            raise ValueError(f"Invalid type {prop_type}")

        # If new val is given lets try to set it and compare it with result
        setattr(obj, attrib, new_value)
        print(f"Checking {attrib} - {prop_type} with '{new_value}'")
        if isinstance(new_value, datetime):
            # We need
            compare: datetime = getattr(obj, attrib)
            assert str(compare.astimezone()) == str(new_value)
        else:
            assert getattr(obj, attrib) == new_value

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

            task = tasks[0]

            # Test printing all
            for attribute in dir(task):
                if not attribute.startswith("_"):
                    print(f"{attribute} = {getattr(task, attribute)}")

            # Test setting attributes based on typed annotation
            for attribute in dir(task):
                if not attribute.startswith("_"):
                    prop_type = get_prop_set_type_annotation(task, attribute)
                    if prop_type in (int, bool, None, datetime, str):
                        check_setting_val(task, attribute, prop_type)
                    elif prop_type == Optional[datetime]:
                        check_setting_val(task, attribute, None)
                        check_setting_val(task, attribute, datetime)
                    else:
                        print(f"{attribute} ignored {prop_type}")
            raise DoNotSave("We do not want the file to save!")
