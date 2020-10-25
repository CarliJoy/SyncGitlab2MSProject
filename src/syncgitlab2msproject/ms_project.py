from os import PathLike
from logging import getLogger
from typing import Sequence, Optional
import dateutil
import pywintypes

import win32com.client
import sys, time, datetime

# Classes to accesss Microsoft Project
# Inspiried by https://gist.github.com/zlorb/ff122e8563793bb28f79
from .exceptions import ClassNotInitiated, LoadingError
from .functions import make_none_safe

debug = True


logger = getLogger("syncgitlab2msproject.ms_project")


@make_none_safe
def win2python_datetime(win32datetime: "pywintypes.datetime") -> datetime:
    """
    Convert MSProject time to Python time

    might be a cumbersome to convert to string first but seems the only way
    to be sure the timezone is correct
    see http://timgolden.me.uk/python/win32_how_do_i/use-a-pytime-value.html
    for an alternative.
    This solution is taken from:
    https://stackoverflow.com/questions/39028290/python-convert-pywintyptes-datetime-to-datetime-datetime
    """
    return dateutil.parser.parse(str(win32datetime))


class MSProject(Sequence):
    """MSProject class."""

    def __init__(self):
        self.project = None
        self._Tasks = None
        self.mpp = win32com.client.Dispatch("MSProject.Application")
        if debug:
            self.mpp.Visible = 1

    def load(self, doc: PathLike) -> None:
        """Load a given MSProject file."""
        try:
            self.mpp.FileOpen(doc)
            self.project = self.mpp.ActiveProject
        except Exception as e:
            logger.exception(f"Error opening file: {doc}")
            raise LoadingError(e)

    def saveAndClose(self) -> None:
        """Close an open MSProject, saving changes."""
        if self.project is not None:
            self.mpp.FileSave()
        self.mpp.Quit()

    def __len__(self) -> int:
        if self.project is None:
            raise ClassNotInitiated("Can't get length for a not loaded project")
        return self.project.Tasks.Count

    def get_task(self, task_nr: int):
        return self.project.Tasks(task_nr + 1)

    def __getitem__(self, i: int) -> Optional["Task"]:
        return Task(self, i)


class Task:
    """
    Python Wrapper Class around MS Project Task API

    Find API reference here:
    https://docs.microsoft.com/office/vba/api/project.task
    """
    def __init__(self, project: MSProject, task_number: int):
        self.project = project
        self.tasknr = task_number

    def _get_task(self):
        return self.project.get_task(self.tasknr)

    @property
    def start(self) -> Optional[datetime]:
        return win2python_datetime(self._get_task().Start)

    @start.setter
    def start(self, value):
        # TODO Implement!
        pass

    @property
    def notes(self) -> str:
        return self._get_task().Notes

    @notes.setter
    def notes(self, value: str):
        self._get_task().Notes = value

    @property
    def duration(self) -> Optional[int]:
        """Gets  the duration (in minutes) of a task.
         Read-only for summary tasks. Read/write Variant."""
        return self._get_task().duration

    @duration.setter
    def duration(self, value):
        pass