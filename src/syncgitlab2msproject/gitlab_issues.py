import dateutil.parser
from datetime import datetime
from gitlab import Gitlab
from logging import getLogger
from typing import List, Optional

from .custom_types import GitlabIssue, GitlabUserDict
from .exceptions import MovedIssueNotDefined

logger = getLogger(f"{__package__}.{__name__}")


def get_user_identifier(user_dict: GitlabUserDict) -> str:
    """
    Return the user identifier

    keep as separate function to allow easier changes later if required
    """
    return str(user_dict["name"])


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

    def __str__(self):
        return f"'{self.title}' (ID: {self.id})"

    # **************************************************************
    # *** Define some default properties to allow static typing  ***
    # **************************************************************
    @property
    def id(self) -> int:
        """
        The id of an issue - it seems to be unique within an installation
        """
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
                # Needed for
                assert self._moved_reference is not None
                return self._moved_reference.percentage_tasks_done
            return 100
        if not self.has_tasks:
            return 0
        task = self.task_completion_status
        return round(task["completed_count"] / task["count"] * 100)

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
        if (val := self.obj.closed_at) is not None:
            return dateutil.parser.parse(val)
        return None

    @property
    def due_date(self) -> Optional[datetime]:
        if (val := self.obj.due_date) is not None:
            return dateutil.parser.parse(val)
        return None

    @property
    def closed_by(self) -> Optional[str]:
        if (val := self.obj.closed_by) is not None:
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
        """
        list of Gitlab Assignees.

        Note in the community edition only one assignee is possible
        """
        return [get_user_identifier(user) for user in self.obj.assignees]

    @property
    def labels(self) -> List[str]:
        """
        list of labels
        """
        return self.obj.labels

    @property
    def web_url(self) -> str:
        """
        give the url from which the issue can be accessed
        """
        return self.obj.web_url


def get_gitlab_class(server: str, personal_token: Optional[str] = None) -> Gitlab:
    if personal_token is None:
        return Gitlab(server)
    else:
        return Gitlab(server, private_token=personal_token)


def get_group_issues(gitlab: Gitlab, group_id: int) -> List[Issue]:
    group = gitlab.groups.get(group_id, lazy=True)
    return [Issue(issue) for issue in group.issues.list(all=True)]


def get_project_issues(gitlab: Gitlab, project_id: int) -> List[Issue]:
    project = gitlab.projects.get(project_id, lazy=True)
    return [Issue(issue) for issue in project.issues.list(all=True)]
