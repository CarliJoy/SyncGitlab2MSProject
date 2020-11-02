from typing import Optional, List
from gitlab import Gitlab
from datetime import datetime

import dateutil.parser
from .custom_types import GitlabIssue, GitlabUserDict

from .exceptions import MovedIssueNotDefined


def get_user_identifier(user_dict: GitlabUserDict) -> str:
    """
    Return the user identifier

    keep as separate function to allow easier changes later if required
    """
    return user_dict["name"]


class Issue:
    """
    Wrapper class around Group/Project Issues
    """

    # The issue object itself is not dynamic only the contained obj is!
    __slots__ = ["obj", "_moved_reference"]

    def __init__(self, obj: GitlabIssue):
        self.obj: GitlabIssue = obj
        self._moved_reference: Optional[Issue] = None

    def __getattr__(self, item: str):
        """Default to get the values from the original objext"""
        return getattr(self.obj, item)

    @property
    def moved_reference(self) -> Optional["Issue"]:
        """
        get the reference to the moved issue if defined

        :exceptions MovedIssueNotDefined
        """
        if self.moved_to_id is None:
            return None
        else:
            if self._moved_reference is None:
                raise MovedIssueNotDefined(
                    "The issue is marked as moved but was not referenced "
                    "in the loaded issues, so tracking is not possible."
                )
            else:
                return self._moved_reference

    @moved_reference.setter
    def moved_reference(self, value: "Issue"):
        if not isinstance(value, Issue):
            raise ValueError("Can only set an Issue object as moved reference!")
        self._moved_reference = value

    # **************************************************************
    # *** Define some default properties to allow static typing  ***
    # **************************************************************
    @property
    def id(self) -> int:
        return self.obj.id

    @property
    def iid(self) -> int:
        return self.obj.iid

    @property
    def project_id(self) -> int:
        return self.obj.project_id

    @property
    def group_id(self) -> int:
        return self.obj.group_id

    @property
    def has_tasks(self) -> bool:
        return self.obj.has_tasks

    @property
    def is_closed(self) -> bool:
        return str(self.obj.state).lower().strip().startswith("closed")

    @property
    def is_open(self):
        return not self.is_closed

    @property
    def percentage_tasks_done(self) -> int:
        """
        Percentage of tasks done, 0 if no tasks are defined and not closed.
        By definition always 100 if issue is closed (and not moved)

        :exceptions MovedIssueNotDefined
        """
        if self.is_closed:
            if self.moved_to_id is not None:
                return self._moved_reference.percentage_tasks_done
            return 100
        if not self.has_tasks:
            return 0
        task = self.task_completion_status
        return round(task["completed_count"] / task["count"])

    @property
    def moved_to_id(self) -> Optional[int]:
        return self.obj.moved_to_id

    @property
    def title(self) -> str:
        return self.obj.title

    @property
    def description(self) -> str:
        return self.obj.description

    @property
    def closed_at(self) -> Optional[datetime]:
        if val := self.obj.closed_at is not None:
            return dateutil.parser.parse(val)
        return None

    @property
    def due_date(self) -> Optional[datetime]:
        if val := self.obj.due_date is not None:
            return dateutil.parser.parse(val)
        return None

    @property
    def closed_by(self) -> Optional[str]:
        if val := self.obj.closed_by is not None:
            return get_user_identifier(val)
        return None

    @property
    def time_estimated(self) -> float:
        """
        Time estimated in minutes
        """
        return self.obj.time_stats["time_estimate"] / 60

    @property
    def time_spent_total(self) -> float:
        """
        Total time spent in minutes
        """
        return self.obj.time_stats["total_time_spent"] / 60

    @property
    def assignees(self) -> List[str]:
        return [get_user_identifier(user) for user in self.obj.assignees]

    @property
    def labels(self) -> List[str]:
        return self.obj.labels


def get_gitlab_class(server: str, personal_token: Optional[str] = None) -> Gitlab:
    if personal_token is None:
        return Gitlab(server)
    else:
        return Gitlab(server, private_token=personal_token)


def get_group_issues(gitlab: Gitlab, group_id: int) -> List[Issue]:
    group = gitlab.groups.get(group_id, lazy=True)
    return [Issue(issue) for issue in group.issues.list(all=True)]
