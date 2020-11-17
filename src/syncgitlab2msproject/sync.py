from typing import List, Dict, Optional
from logging import getLogger

import win32com.universal
from syncgitlab2msproject.custom_types import WebURL

from .exceptions import MovedIssueNotDefined, MSProjectValueSetError
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
    if task is not None:
        if (url := task.hyperlink_address) is not None:
            url = WebURL(url)
        # If not as hyperlink we also look in task.text29 field
        elif (url := task.text29) is not None:
            url = WebURL(url)
        if is_gitlab_hyperlink(url, gitlab_url):
            return url
    return None


def update_task_with_issue_data(
    task: Task, issue: Issue, parent_ids: Optional[List[IssueRef]] = None
) -> List[IssueRef]:
    """
    Update task with issue data

    if an issue is moved the date of the new issue is used as long it is available

    Args:
        task: The MS Project task that will be updated
        issue: the issue with the data to be considered
        parent_ids: the parent stuff

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
            return update_task_with_issue_data(task, moved_ref, parent_ids)
        except MovedIssueNotDefined:
            logger.warning(
                f"Issue {issue} was moved outside of context."
                f" Ignoring the issue. Please update the task {task} manually!"
            )
    else:
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
    # Add a setting to allow forcing outline level on new tasks
    # task.outline_level = 1
    update_task_with_issue_data(task, issue)


def sync_gitlab_issues_to_ms_project(
    tasks: MSProject, issues: List[Issue], gitlab_url: WebURL
):
    """

    Args:
        tasks: MS Project Tasks that will be synchronized
        issues:  List of Gitlab Issues
        gitlab_url: the gitlab istance url to check url found in MS project against

    Returns:

    """
    # Keep track of already synced issues
    synced: List[IssueRef] = []

    # Create Dictionary of all IDs to find moved ones and relate existing
    ref_id_to_issue: Dict[IssueRef, Issue] = {
        get_issue_ref_id(issue): issue for issue in issues
    }
    # We also try to sync according to the weburl but only in a second step
    web_url_to_issue: Dict[WebURL, Issue] = {
        get_issue_web_url(issue): issue for issue in issues
    }

    # Find moved issues and reference them
    non_moved: List[IssueRef] = []
    for issue in issues:
        if (ref_int_id := issue.moved_to_id) is not None:
            if (ref_id := IssueRef(ref_int_id)) in ref_id_to_issue:
                issue.moved_reference = ref_id_to_issue[ref_id]
        else:
            non_moved.append(get_issue_ref_id(issue))

    # get existing references and update them
    for task in tasks:
        if task is None:
            continue
        array_to_check = None
        if (ref_id2 := get_issue_ref_from_task(task)) is not None:
            array_to_check = ref_id_to_issue
        # if the normal ID was not found try if a webtask was found
        elif (ref_id2 := get_weburl_from_task(task, gitlab_url)) is not None:
            array_to_check = web_url_to_issue

        if array_to_check is not None:
            try:
                issue = ref_id_to_issue[ref_id2]
            except KeyError:
                logger.warning(
                    f"Task {task} refers to Issue {ref_id2} which was not loaded."
                    f" --> Ignored."
                )
            else:
                synced += update_task_with_issue_data(task, issue)

    # adding everything that was not synced and is not duplicate
    for ref_id in non_moved:
        if ref_id not in synced:
            add_issue_as_task_to_project(tasks, ref_id_to_issue[ref_id])
