from typing import List, Dict, Optional, overload, Callable
from logging import getLogger

import win32com.universal
from syncgitlab2msproject.custom_types import WebURL

from .exceptions import (
    MovedIssueNotDefined,
    MSProjectValueSetError,
    IssueReferenceDuplicated,
)
from .gitlab_issues import Issue
from .ms_project import Task, MSProject
from .custom_types import IssueRef

logger = getLogger(f"{__package__}.{__name__}")

GL_PREFIX = "!!DO NOT CHANGE!! Gitlab:"

DEFAULT_DURATION = 8 * 60


def get_issue_ref_id(issue: Issue) -> IssueRef:
    """
    Return the ID of an gitlab issue

    Note the
    """
    return IssueRef(issue.id)


def get_issue_web_url(issue: Issue) -> WebURL:
    """
    Get the web url from an gitlab issue
    """
    return WebURL(issue.web_url)


def set_issue_ref_to_task(task: Task, issue: Issue) -> None:
    """set reference to gitlab issues in MS Project task"""
    task.text30 = (
        f"{GL_PREFIX}{issue.id};{issue.group_id};{issue.project_id};{issue.iid}"
    )


def get_issue_ref_from_task(task: Optional[Task]) -> Optional[IssueRef]:
    """get reference to gitlab issues from MS Project task"""
    if task is not None and task.text30 and task.text30.startswith(GL_PREFIX):
        values = task.text30[len(GL_PREFIX) :].split(";")
        return IssueRef(int(values[0]))
    return None


def is_gitlab_hyperlink(url: WebURL, gitlab_url: WebURL) -> bool:
    return url.startswith(gitlab_url)


def get_weburl_from_task(task: Optional[Task], gitlab_url: WebURL) -> Optional[WebURL]:
    """
    Get the weburl from MS Project Task (is saved as hyperlink)
    """

    def check_get_url(value: Optional[str]) -> Optional[WebURL]:
        if value is not None:
            check_url = WebURL(value)
            if is_gitlab_hyperlink(check_url, gitlab_url):
                return check_url
        return None

    if task is not None:
        if (url := check_get_url(task.hyperlink_address)) is not None:
            return url
        # If not as hyperlink we also look in task.text29 field
        if (url := check_get_url(task.text29)) is not None:
            return url
    return None


def update_task_with_issue_data(
    task: Task,
    issue: Issue,
    *,
    parent_ids: Optional[List[IssueRef]] = None,
    ignore_issue: bool = False,
) -> List[IssueRef]:
    """
    Update task with issue data

    if an issue is moved the date of the new issue is used as long it is available

    Args:
        task: The MS Project task that will be updated
        issue: the issue with the data to be considered
        parent_ids: the parent stuff
        ignore_issue: only return the related (and moved) ids but do not really sync
                      This is required so we can ignored also moved issues correctly

    Returns:
        list of IssueRefs that
    """
    if parent_ids is None:
        parent_ids = [get_issue_ref_id(issue)]
    else:
        parent_ids += [get_issue_ref_id(issue)]

    if (moved_ref := issue.moved_reference) is not None:
        assert moved_ref is not None
        try:
            return update_task_with_issue_data(
                task, moved_ref, parent_ids=parent_ids, ignore_issue=ignore_issue
            )
        except MovedIssueNotDefined:
            logger.warning(
                f"Issue {issue} was moved outside of context."
                f" Ignoring the issue. Please update the task {task} manually!"
            )
    elif not ignore_issue:
        set_issue_ref_to_task(task, issue)
        try:
            task.name = issue.title
            task.notes = issue.description
            if issue.due_date is not None:
                task.deadline = issue.due_date
            if issue.has_tasks or task.percent_complete == 0:
                task.percent_complete = issue.percentage_tasks_done
            task.work = int(issue.time_estimated)
            # Update duration in case it seems to be default
            if task.duration == DEFAULT_DURATION and task.estimated:
                if task.work > 0:
                    task.duration = task.work
            task.actual_work = issue.time_spent_total
            task.hyperlink_name = "Open in Gitlab"
            task.hyperlink_address = issue.web_url
            task.text29 = issue.web_url
            task.text28 = "; ".join([f'"{label}"' for label in issue.labels])
            if issue.is_closed:
                task.actual_finish = issue.closed_at
        except (MSProjectValueSetError, win32com.universal.com_error) as e:
            logger.error(
                f"FATAL: Could not sync issue {issue} to task {task}.\nError: {e}"
            )
        else:
            logger.info(f"Synced issue {issue} to task {task}")
    return parent_ids


def add_issue_as_task_to_project(tasks: MSProject, issue: Issue):
    task = tasks.add_task(issue.title)
    logger.info(f"Created {task} as it was missing for issue, now syncing it.")
    # Add a setting to allow forcing outline level on new tasks
    # task.outline_level = 1
    update_task_with_issue_data(task, issue)


class IssueFinder:
    def __init__(self, issues: List[Issue]):
        # Create Dictionary of all IDs to find moved ones and relate existing
        self.ref_id_to_issue: Dict[IssueRef, Issue] = {}
        # We also try to sync according to the weburl but only in a second step
        self.web_url_to_issue: Dict[WebURL, Issue] = {}
        for issue in issues:
            """ Set up all references to locate later on"""
            ref_id = get_issue_ref_id(issue)
            if ref_id in self.ref_id_to_issue:
                raise IssueReferenceDuplicated(
                    f"Reference ID {ref_id} was already defined! "
                    f"{self.ref_id_to_issue[ref_id]} and {issue} "
                    f"share the same Reference ID"
                )
            self.ref_id_to_issue[ref_id] = issue

            web_url = get_issue_web_url(issue)
            if web_url in self.web_url_to_issue:
                raise IssueReferenceDuplicated(
                    f"Web URL {web_url} was already defined! "
                    f"{self.web_url_to_issue[web_url]} and {issue} "
                    f"share the same Web URL"
                )
            self.web_url_to_issue[web_url] = issue

    # Overload to make mypy aware of the fact that only None is given
    # once the id is none
    @overload
    def by_ref_id(self, ref_id: IssueRef) -> Issue:
        ...

    @overload
    def by_ref_id(self, ref_id: None) -> None:
        ...

    def by_ref_id(self, ref_id: Optional[IssueRef]) -> Optional[Issue]:
        """
        Give related issue if ref_id is set and the issue is found
        If an invalid reference is given throw
        :exceptions KeyError
        """
        if ref_id is None:
            return None
        return self.ref_id_to_issue[ref_id]

    def by_web_url(self, web_url: Optional[WebURL]) -> Optional[Issue]:
        """
        Give related issue if weburl is set and the issue is found,
        If an invalid web_url is given throw
        :exceptions KeyError
        """
        if web_url is None:
            return None
        return self.web_url_to_issue[web_url]


def find_related_issue(
    task: Task, find_issue: IssueFinder, gitlab_url: WebURL
) -> Optional[Issue]:
    try:
        if (issue := find_issue.by_ref_id(get_issue_ref_from_task(task))) is not None:
            return issue
    except KeyError as key:
        logger.warning(
            f"Task {task} refers to Issue with ID {key} which was not found in ."
            f"the issues loaded from gitlab --> Ignored this reference"
        )
    try:
        if (
            issue := find_issue.by_web_url(get_weburl_from_task(task, gitlab_url))
        ) is not None:
            return issue
    except KeyError as key:
        logger.warning(
            f"Task {task} refers to Web url {key} which was not found in ."
            f"the issues loaded from gitlab --> Ignored this reference"
        )
    return None


def sync_gitlab_issues_to_ms_project(
    tasks: MSProject,
    issues: List[Issue],
    gitlab_url: WebURL,
    include_issue: Optional[Callable[[Issue], bool]] = None,
) -> None:
    """

    Args:
        tasks: MS Project Tasks that will be synchronized
        issues:  List of Gitlab Issues
        gitlab_url: the gitlab istance url to check url found in MS project against
        include_issue: Include issue in sync, if None include everything
    """
    if include_issue is None:
        include_issue = lambda x: True

    ref_issue: Optional[Issue]
    # Keep track of already synced issues
    synced: List[IssueRef] = []

    # create finder
    find_issue = IssueFinder(issues)

    # Find moved issues and reference them
    non_moved: List[IssueRef] = []
    for issue in issues:
        if (ref_int_id := issue.moved_to_id) is not None:
            if (ref_issue := find_issue.by_ref_id(IssueRef(ref_int_id))) is not None:
                issue.moved_reference = ref_issue
        else:
            non_moved.append(get_issue_ref_id(issue))

    # get existing references and update them
    for task in tasks:
        if task is None:
            continue
        ref_issue = find_related_issue(task, find_issue, gitlab_url)

        if ref_issue is None:
            logger.info(
                f"Not Syncing {task} as a not reference "
                f"to an gitlab issue could be found"
            )
        else:
            ignore_issue = False
            if not include_issue(ref_issue):
                logger.info(
                    f"Ignoring task {task} as issue {ref_issue} "
                    f"has been marked to be ignored"
                )
                ignore_issue = True
            else:
                logger.info(f"Syncing {ref_issue} into {task}")
            # We want to not have the ignored task popping up in issues that need to be
            # added and we also want make sure that moved ignored issues are handled
            # correctly
            synced += update_task_with_issue_data(
                task, ref_issue, ignore_issue=ignore_issue
            )

    # adding everything that was not synced and is not duplicate
    for ref_id in non_moved:
        if ref_id not in synced:
            if (ref_issue := find_issue.by_ref_id(ref_id)) is not None:
                if not include_issue(ref_issue):
                    logger.info(
                        f"Do not add issue {ref_issue} "
                        f"as it has been marked to be ignored."
                    )
                else:
                    add_issue_as_task_to_project(tasks, ref_issue)
