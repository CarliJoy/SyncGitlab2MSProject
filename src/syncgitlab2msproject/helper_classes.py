from abc import ABC, abstractmethod
from typing import Optional

from .gitlab_issues import Issue
from .ms_project import PjTaskFixedType, Task


class TaskTyperSetter(ABC):
    """
    Abstract Base Class that is used to dynamically allow setting the task type
    """

    def __init__(self, issue: Issue) -> None:
        self._type_before_sync: Optional[PjTaskFixedType] = None
        self._effort_driven_before_sync: Optional[bool] = None
        self._is_initial: bool = False
        self.issue = Issue

    @abstractmethod
    def set_task_type_before_sync(self, task: Task, is_initial: bool) -> None:
        """
        Function that is called at the beginning of the sync
        """

    @abstractmethod
    def set_task_type_after_sync(self, task: Task) -> None:
        """
        Function just before finishing the sync
        """


class SetTaskTypeConservative(TaskTyperSetter):
    """
    Set Fixed Work as default creating a new task and before syncing any Task
    but make sure to reset to the original value (including Effort Driven Setting)
    after finishing the sync
    """

    def set_task_type_before_sync(self, task: Task, is_inital: bool) -> None:
        if task.has_children:
            # Can't update tasks with children
            return
        self._type_before_sync = task.type
        self._effort_driven_before_sync = task.effort_driven
        self._is_initial = is_inital
        task.type = PjTaskFixedType.pjFixedWork

    def set_task_type_after_sync(self, task: Task) -> None:
        if task.has_children:
            # Can't update tasks with children
            return
        if not self._is_initial:
            assert self._effort_driven_before_sync is not None
            assert self._type_before_sync is not None
            # Only update if required
            if task.type != self._type_before_sync:
                task.type = self._type_before_sync
            if task.effort_driven != self._effort_driven_before_sync:
                task.effort_driven = self._effort_driven_before_sync


class ForceFixedWork(SetTaskTypeConservative):
    """
    No matter what always set Task Type to Fixed Work for all synced Task
    """

    def set_task_type_after_sync(self, task: Task) -> None:
        # Make sure the everything is FixedWork by default by not resetting it
        pass
