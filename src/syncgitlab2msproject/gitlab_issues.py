import dateutil.parser
from datetime import datetime
from functools import lru_cache
from gitlab import Gitlab
from gitlab.v4.objects import Project
from logging import getLogger
from typing import Dict, List, Optional, Union

from .custom_types import GitlabIssue, GitlabUserDict
from .exceptions import MovedIssueNotDefined
from .funcions import warn_once

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
    __slots__ = [
        "obj",
        "_moved_reference",
        "_fixed_group_id",
    ]

    def __init__(self, obj: GitlabIssue, fixed_group_id: Optional[int] = None):
        """
        :param obj:
        :param fixed_group_id: Do not extract the group_id from the
                               Gitlab issue but assume it is fixed
        """
        self._fixed_group_id = fixed_group_id
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
    def group_id(self) -> Optional[int]:
        """
        Return the group id, if negative a user id is given
        The group ID is either taken from the issue itself or if a project is given
        the issue is fixed (see #7)

        If group_id isn't fixed and can't be extracted, only give a warning and do
        not fail, as it isn't required to have the sync working. Only the
        issue id or weblink is used to find the related issue.
        See `sync.py`
          * `get_issue_ref_from_task`
          * `IssueFinder`

        """
        if self._fixed_group_id is not None:
            return self._fixed_group_id
        try:
            return self.obj.group_id
        except AttributeError:
            warn_once(
                logger,
                "Could not extract group_id from Issue. "
                "This is not required for syncing, so I will continue.",
            )
            return None

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
    def created_at(self) -> Optional[datetime]:
        if (val := self.obj.created_at) is not None:
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

    def _get_from_time_stats(self, key) -> Optional[float]:
        """
        Somehow the python-gitlab API seems to be not 100% fixed,
        see issue #9

        :param key: key to query from time stats
        :return: the value if existing or none
        """
        query_dict: Dict[str, float]
        if callable(self.obj.time_stats):
            query_dict = self.obj.time_stats()
        else:
            query_dict = self.obj.time_stats
        return query_dict.get(key, None)

    @property
    def time_estimated(self) -> Optional[float]:
        """
        Time estimated in minutes
        """
        if (time_estimate := self._get_from_time_stats("time_estimate")) is not None:
            return time_estimate / 60
        else:
            logger.warning("Time Estimate is None")
            return None

    @property
    def time_spent_total(self) -> Optional[float]:
        """
        Total time spent in minutes
        """
        if (time_spend := self._get_from_time_stats("total_time_spent")) is not None:
            return time_spend / 60
        else:
            logger.warning("Time spend is None")
            return None

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
    def full_ref(self) -> str:
        """
        give the full reference through which the issue can be accessed
        """
        return self.obj.attributes['references']['full']

    @property
    def web_url(self) -> str:
        """
        give the url from which the issue can be accessed
        """
        return self.obj.web_url

@lru_cache(10)
def get_group_id_from_gitlab_project(project: Project) -> Optional[int]:
    """
    Get user id form gitlab project.
    If the namespace of the project is a user, a negativ
    value is returned
    :param project:
    """
    try:
        namespace: Dict[str, Union[int, str]] = project.namespace
    except AttributeError:
        logger.warning(
            f"Could not extract name space for project '{project.get_id()}' - "
            "This error will be ignored."
        )
        return None
    if str(namespace["kind"]).lower() == "user":
        return -int(namespace["id"])
    else:
        return int(namespace["id"])


def get_gitlab_class(server: str, personal_token: Optional[str] = None) -> Gitlab:
    if personal_token is None:
        return Gitlab(server, ssl_verify=False)
    else:
        return Gitlab(server, private_token=personal_token, ssl_verify=False)


def get_group_issues(gitlab: Gitlab, group_id: int) -> List[Issue]:
    group = gitlab.groups.get(group_id, lazy=True)
    return [Issue(issue) for issue in group.issues.list(all=True)]


def get_project_issues(gitlab: Gitlab, project_id: int) -> List[Issue]:
    project = gitlab.projects.get(project_id)
    return [
        Issue(issue, fixed_group_id=get_group_id_from_gitlab_project(project))
        for issue in project.issues.list(all=True)
    ]
