# -*- coding: utf-8 -*-

from syncgitlab2msproject.ms_project import MSProject
from pathlib import Path

__author__ = "Carli"
__copyright__ = "Carli"
__license__ = "mit"


BASE_DIR = Path(__file__).absolute().parent
TEST_FILE = BASE_DIR / "Project1.mpp"


def test_printing_all():
    assert TEST_FILE.is_file()
    print(f"Loading '{TEST_FILE}'")
    with MSProject(TEST_FILE) as tasks:
        print(len(tasks))
        for task in tasks:
            if task:
                print(task.name)
