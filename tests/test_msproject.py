# -*- coding: utf-8 -*-
import pytest

from datetime import datetime
from functools import partial
from inspect import getattr_static, signature
from pathlib import Path
from typing import Any, Callable, Generic, Type, Union

from syncgitlab2msproject.exceptions import (
    ClassNotInitiated,
    LoadingError,
    MSProjectSyncError,
)
from syncgitlab2msproject.ms_project import MSProject, PjTaskFixedType

__author__ = "Carli"
__copyright__ = "Carli"
__license__ = "MIT"

# Source: https://stackoverflow.com/a/58841311/3813064
# Python >= 3.8
try:
    from typing import get_args, get_origin
# Compatibility
except ImportError:

    def get_args(t: Type):
        return getattr(t, "__args__", ()) if t is not Generic else Generic

    def get_origin(t: Type):
        return getattr(t, "__origin__", None)


def is_optional(field: Type):
    return get_origin(field) is Union and type(None) in get_args(field)


def is_datetime(field: Type):
    return (field == datetime) or (
        get_origin(field) is Union and datetime in get_args(field)
    )


BASE_DIR = Path(__file__).absolute().parent
TEST_FILE_NAME = "Project1.mpp"
TEST_FILE = BASE_DIR / TEST_FILE_NAME


class DoNotSave(Exception):
    pass


# TODO Set up Pytest with copying the Test file
# TODO Make sure that the copied file was not modified
#           --> https://docs.pytest.org/en/stable/fixture.html
# TODO test saving and loading


def get_prop_setter_func(obj: Any, property_name: str) -> Callable:
    return getattr_static(obj, property_name).fset


def get_prop_set_type_annotation(setter_function: Callable) -> Union[str, type]:
    """
    Get the type annotation of obj for property
    """

    # Combination of
    # https://stackoverflow.com/a/9917213/3813064 and
    # https://stackoverflow.com/questions/53949473/python-dynamically-access-type-annotation-of-a-property
    sign = signature(setter_function)
    return next(reversed(sign.parameters.values())).annotation


def test_load_manually():
    project = MSProject(TEST_FILE)
    project.load()
    print(project[0].name)
    assert TEST_FILE_NAME in repr(project[0])
    project.close()


def test_not_loaded():
    project: MSProject = MSProject(TEST_FILE)
    assert "not loaded" in repr(project)
    with pytest.raises(ClassNotInitiated):
        print(project[0].name)
    project.close()


def test_loading_wrong_file():
    with pytest.raises(LoadingError):
        with MSProject(BASE_DIR / "not_existing.mpp"):
            pass


def test_printing_all():
    assert TEST_FILE.is_file()
    print(f"Loading '{TEST_FILE}'")

    with MSProject(TEST_FILE) as tasks:
        assert TEST_FILE_NAME in repr(tasks)
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


def test_setting_everything():
    def do_check_setting_val(
        new_value: Any, obj_to_test: Any, attrib: str, prop_type: Union[type, None]
    ):
        # If new val is given lets try to set it and compare it with result
        setattr(obj_to_test, attrib, new_value)
        print(f"Checking {attrib} - {prop_type} with '{new_value}'")
        if isinstance(new_value, datetime):
            # We need
            compare: datetime = getattr(obj_to_test, attrib)
            assert str(compare.astimezone()) == str(new_value)
        else:
            assert getattr(obj_to_test, attrib) == new_value

    def check_setting_val(obj: Any, attrib: str, prop_type: Union[type, None]):
        check_set_val = partial(
            do_check_setting_val, obj_to_test=obj, attrib=attrib, prop_type=prop_type
        )

        if is_datetime(prop_type):
            do_check_setting_val(
                datetime(2020, 3, 4, 20, 15, 30).astimezone(),
                obj_to_test=obj,
                attrib=attrib,
                prop_type=datetime,
            )
            if is_optional(prop_type):
                do_check_setting_val(
                    None, obj_to_test=obj, attrib=attrib, prop_type=None
                )
        elif prop_type == int:
            check_set_val(1)
        elif prop_type == str:
            check_set_val("Test String")
        elif prop_type == bool:
            check_set_val(True)
            check_set_val(False)
        elif prop_type is None:
            check_set_val(None)
        elif PjTaskFixedType in get_args(prop_type):
            for itm in PjTaskFixedType:
                do_check_setting_val(
                    itm,
                    obj_to_test=obj,
                    attrib=attrib,
                    prop_type=PjTaskFixedType,
                )
                do_check_setting_val(
                    itm,
                    obj_to_test=obj,
                    attrib=attrib,
                    prop_type=int,
                )
        else:
            raise ValueError(f"Invalid type {prop_type}")

    with pytest.raises(DoNotSave):
        with MSProject(TEST_FILE) as tasks:
            # Test setting attributes based on typed annotation
            task = tasks[0]
            for attribute in dir(task):
                if not attribute.startswith("_"):
                    if setter_func := get_prop_setter_func(task, attribute):
                        prop_type = get_prop_set_type_annotation(setter_func)
                        check_setting_val(task, attribute, prop_type)
            raise DoNotSave("We do not want the file to save!")


def test_percentage():
    with pytest.raises(MSProjectSyncError):
        with MSProject(TEST_FILE) as tasks:
            # Test setting attributes based on typed annotation
            task = tasks[0]
            task.percent_complete = 101
