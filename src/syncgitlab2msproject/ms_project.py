from os import PathLike
from logging import getLogger
from typing import Sequence, Optional, Union
from datetime import datetime
import dateutil
import pywintypes

import win32com.client

# Classes and functions to access Microsoft Project
# Inspired by https://gist.github.com/zlorb/ff122e8563793bb28f79
from win32com.universal import com_error

from .exceptions import ClassNotInitiated, LoadingError, MSProjectSyncError
from .decorators import make_none_safe

debug = True


logger = getLogger(f"{__package__}.{__name__}")


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


def na_win2py_datetime(win32datetime: "pywintypes.datetime") -> Optional[datetime]:
    """
    Convert also NA datetime to Python Datetype, give None if NA
    """
    if isinstance(win32datetime, str) and win32datetime.lower() == "na":
        return None
    else:
        return win2python_datetime(win32datetime)


def na_py2win_datetime(dt: Optional[datetime]) -> Union[datetime, str]:
    """
    Convert nullable datetype for usage in MS Project
    """
    if dt is None:
        return "NA"
    else:
        return dt


class MSProject(Sequence):
    """MSProject class."""

    def __init__(self, doc_path: PathLike):
        self.project = None
        self.mpp = win32com.client.Dispatch("MSProject.Application")
        self.doc_path: PathLike = doc_path
        if debug:
            self.mpp.Visible = 1

    def __repr__(self):
        if self.project is None:
            return "<MSProject(not loaded)>"
        else:
            return f"<MSProject('{self.project.Name}')>"

    def __enter__(self):
        self.load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Only save on success
        if exc_type is None:
            self.save_and_close()
        else:
            self.close()

    def load(self) -> None:
        """Load a given MSProject file."""
        try:
            self.mpp.FileOpen(str(self.doc_path))
            self.project = self.mpp.ActiveProject
        except Exception as e:
            logger.exception(f"Error opening file: {self.doc_path}")
            raise LoadingError(e)

    def close(self) -> None:
        """Forces a close without saving (has to be done manually)"""
        if self.project is not None:
            try:
                self.mpp.FileClose(False)
            except com_error as e:
                logger.info(f"File close failed: {e}")
        self.mpp.Quit()
        del self.mpp

    def save_and_close(self) -> None:
        """Close an open MSProject, saving changes."""
        if self.project is not None:
            self.mpp.FileSave()
        self.close()

    def __len__(self) -> int:
        if self.project is None:
            raise ClassNotInitiated("Can't get length for a not loaded project")
        return self.project.Tasks.Count

    def get_task(self, task_nr: int):
        return self.project.Tasks(task_nr + 1)

    def __getitem__(self, i: int) -> Optional["Task"]:
        if i >= len(self):
            raise IndexError("Out of tasks")
        if self.get_task(i) is None:
            return None
        else:
            return Task(self, i)


class Task:
    """
    Python Wrapper Class around MS Project Task API

    Find API reference here:
    https://docs.microsoft.com/office/vba/api/project.task

    this helps to use the Task object in a pythonic way, converting all values
    automatically.
    Properties naming follows PEP8 (lower case naming)
    """
    __slots__ = ('_project', '_tasknr')

    def __init__(self, project: MSProject, task_number: int):
        self._project = project
        self._tasknr = task_number

    def __repr__(self):
        return f"<Task({self._project.__repr__()}, {self._tasknr}) '{self.name}'>"

    def _get_task(self):
        return self._project.get_task(self._tasknr)

    @property
    def name(self) -> str:
        return self._get_task().Name

    @name.setter
    def name(self, value: str):
        self._get_task().Name = value

    @property
    def start(self) -> datetime:
        return win2python_datetime(self._get_task().Start)

    @start.setter
    def start(self, value: datetime):
        self._get_task().Start = value

    @property
    def finish(self) -> datetime:
        return win2python_datetime(self._get_task().Finish)

    @finish.setter
    def finish(self, value: datetime):
        self._get_task().Finish = value

    @property
    def actual_start(self) -> Optional[datetime]:
        return na_win2py_datetime(self._get_task().ActualStart)

    @actual_start.setter
    def actual_start(self, value: Optional[datetime]):
        self._get_task().ActualStart = na_py2win_datetime(value)

    @property
    def actual_finish(self) -> Optional[datetime]:
        return na_win2py_datetime(self._get_task().ActualFinish)

    @actual_finish.setter
    def actual_finish(self, value: Optional[datetime]):
        self._get_task().ActualFinish = na_py2win_datetime(value)

    @property
    def deadline(self) -> Optional[datetime]:
        return na_win2py_datetime(self._get_task().Deadline)

    @deadline.setter
    def deadline(self, value: Optional[datetime]):
        self._get_task().Deadline = na_py2win_datetime(value)

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
    def duration(self, value: int):
        self._get_task().duration = value

    @property
    def percent_complete(self) -> int:
        return self._get_task().PercentComplete

    @percent_complete.setter
    def percent_complete(self, value: int):
        if isinstance(value, int) and 0 <= value <= 100:
            self._get_task().PercentComplete = value
        else:
            raise MSProjectSyncError(
                "Attribute percent_complete must be an integer between 0 and 100"
            )

    @property
    def work(self) -> int:
        """Gets or sets the work (in minutes) for the task. Read/write Variant."""
        return self._get_task().Work

    @work.setter
    def work(self, value: int):
        self._get_task().Work = value

    @property
    def actual_work(self):
        """
        Gets or sets the actual work (in minutes) for the task.
        Read/write Variant.
        """
        return self._get_task().ActualWork

    @actual_work.setter
    def actual_work(self, value: int):
        self._get_task().ActualWork = value

    @property
    def estimated(self) -> bool:
        """
        True if the task duration is an estimate.
        False if the task duration is a set value. Read/write Variant.
        """
        return self._get_task().Estimated

    @estimated.setter
    def estimated(self, value: bool):
        self._get_task().Estimated = value

    @property
    def text1(self) -> str:
        """get or sets the Text1 Property"""
        return self._get_task().Text1

    @text1.setter
    def text1(self, value: str):
        self._get_task().Text1 = value

    @property
    def text2(self) -> str:
        """get or sets the Text2 Property"""
        return self._get_task().Text2

    @text2.setter
    def text2(self, value: str):
        self._get_task().Text2 = value

    @property
    def text3(self) -> str:
        """get or sets the Text3 Property"""
        return self._get_task().Text3

    @text3.setter
    def text3(self, value: str):
        self._get_task().Text3 = value

    @property
    def text4(self) -> str:
        """get or sets the Text4 Property"""
        return self._get_task().Text4

    @text4.setter
    def text4(self, value: str):
        self._get_task().Text4 = value

    @property
    def text5(self) -> str:
        """get or sets the Text5 Property"""
        return self._get_task().Text5

    @text5.setter
    def text5(self, value: str):
        self._get_task().Text5 = value

    @property
    def text6(self) -> str:
        """get or sets the Text6 Property"""
        return self._get_task().Text6

    @text6.setter
    def text6(self, value: str):
        self._get_task().Text6 = value

    @property
    def text7(self) -> str:
        """get or sets the Text7 Property"""
        return self._get_task().Text7

    @text7.setter
    def text7(self, value: str):
        self._get_task().Text7 = value

    @property
    def text8(self) -> str:
        """get or sets the Text8 Property"""
        return self._get_task().Text8

    @text8.setter
    def text8(self, value: str):
        self._get_task().Text8 = value

    @property
    def text9(self) -> str:
        """get or sets the Text9 Property"""
        return self._get_task().Text9

    @text9.setter
    def text9(self, value: str):
        self._get_task().Text9 = value

    @property
    def text10(self) -> str:
        """get or sets the Text10 Property"""
        return self._get_task().Text10

    @text10.setter
    def text10(self, value: str):
        self._get_task().Text10 = value

    @property
    def text11(self) -> str:
        """get or sets the Text11 Property"""
        return self._get_task().Text11

    @text11.setter
    def text11(self, value: str):
        self._get_task().Text11 = value

    @property
    def text12(self) -> str:
        """get or sets the Text12 Property"""
        return self._get_task().Text12

    @text12.setter
    def text12(self, value: str):
        self._get_task().Text12 = value

    @property
    def text13(self) -> str:
        """get or sets the Text13 Property"""
        return self._get_task().Text13

    @text13.setter
    def text13(self, value: str):
        self._get_task().Text13 = value

    @property
    def text14(self) -> str:
        """get or sets the Text14 Property"""
        return self._get_task().Text14

    @text14.setter
    def text14(self, value: str):
        self._get_task().Text14 = value

    @property
    def text15(self) -> str:
        """get or sets the Text15 Property"""
        return self._get_task().Text15

    @text15.setter
    def text15(self, value: str):
        self._get_task().Text15 = value

    @property
    def text16(self) -> str:
        """get or sets the Text16 Property"""
        return self._get_task().Text16

    @text16.setter
    def text16(self, value: str):
        self._get_task().Text16 = value

    @property
    def text17(self) -> str:
        """get or sets the Text17 Property"""
        return self._get_task().Text17

    @text17.setter
    def text17(self, value: str):
        self._get_task().Text17 = value

    @property
    def text18(self) -> str:
        """get or sets the Text18 Property"""
        return self._get_task().Text18

    @text18.setter
    def text18(self, value: str):
        self._get_task().Text18 = value

    @property
    def text19(self) -> str:
        """get or sets the Text19 Property"""
        return self._get_task().Text19

    @text19.setter
    def text19(self, value: str):
        self._get_task().Text19 = value

    @property
    def text20(self) -> str:
        """get or sets the Text20 Property"""
        return self._get_task().Text20

    @text20.setter
    def text20(self, value: str):
        self._get_task().Text20 = value

    @property
    def text21(self) -> str:
        """get or sets the Text21 Property"""
        return self._get_task().Text21

    @text21.setter
    def text21(self, value: str):
        self._get_task().Text21 = value

    @property
    def text22(self) -> str:
        """get or sets the Text22 Property"""
        return self._get_task().Text22

    @text22.setter
    def text22(self, value: str):
        self._get_task().Text22 = value

    @property
    def text23(self) -> str:
        """get or sets the Text23 Property"""
        return self._get_task().Text23

    @text23.setter
    def text23(self, value: str):
        self._get_task().Text23 = value

    @property
    def text24(self) -> str:
        """get or sets the Text24 Property"""
        return self._get_task().Text24

    @text24.setter
    def text24(self, value: str):
        self._get_task().Text24 = value

    @property
    def text25(self) -> str:
        """get or sets the Text25 Property"""
        return self._get_task().Text25

    @text25.setter
    def text25(self, value: str):
        self._get_task().Text25 = value

    @property
    def text26(self) -> str:
        """get or sets the Text26 Property"""
        return self._get_task().Text26

    @text26.setter
    def text26(self, value: str):
        self._get_task().Text26 = value

    @property
    def text27(self) -> str:
        """get or sets the Text27 Property"""
        return self._get_task().Text27

    @text27.setter
    def text27(self, value: str):
        self._get_task().Text27 = value

    @property
    def text28(self) -> str:
        """get or sets the Text28 Property"""
        return self._get_task().Text28

    @text28.setter
    def text28(self, value: str):
        self._get_task().Text28 = value

    @property
    def text29(self) -> str:
        """get or sets the Text29 Property"""
        return self._get_task().Text29

    @text29.setter
    def text29(self, value: str):
        self._get_task().Text29 = value

    @property
    def text30(self) -> str:
        """get or sets the Text30 Property"""
        return self._get_task().Text30

    @text30.setter
    def text30(self, value: str):
        self._get_task().Text30 = value
