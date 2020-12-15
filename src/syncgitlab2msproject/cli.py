# -*- coding: utf-8 -*-
"""
Handle the Command Line Interface
"""

import argparse
import functools
import logging
import sys
from pathlib import Path
from requests import ConnectionError
from typing import List

from syncgitlab2msproject import Issue, MSProject, __version__

__author__ = "Carli Freudenberg"
__copyright__ = "Carli Freudenberg"
__license__ = "MIT"

from syncgitlab2msproject.custom_types import WebURL
from syncgitlab2msproject.gitlab_issues import (
    get_gitlab_class,
    get_group_issues,
    get_project_issues,
)
from syncgitlab2msproject.helper_classes import ForceFixedWork, SetTaskTypeConservative
from syncgitlab2msproject.sync import sync_gitlab_issues_to_ms_project

_logger = logging.getLogger(f"{__package__}.{__name__}")


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Sync Gitlab Issue into MS Project ")
    parser.add_argument(
        "--version",
        action="version",
        version="SyncGitlab2MSProject {ver}".format(ver=__version__),
    )

    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )

    parser.add_argument(
        "--ignore-label",
        "-i",
        dest="ignore_label",
        help="Ignore Gitlab Issue with a match to the label",
        default="",
        type=str,
    )

    parser.add_argument(
        "--force-fixed-work",
        dest="fixed_work",
        help="Set all synced issued to fixed_work, overwriting "
        "also already existing tasks",
        action="store_true",
    )

    # TODO read from ENV
    parser.add_argument(
        "--gitlab-url",
        "-u",
        dest="gitlab_url",
        help="URL to the gitlab instance i.e. https://gitlab.your-company.com",
        default="https://gitlab.com",
        type=str,
    )

    # TODO read from ENV
    parser.add_argument(
        "--gitlab-token",
        "-t",
        dest="gitlab_token",
        help="Gitlab personal access token",
        default=None,
    )

    parser.add_argument(
        "gitlab_resource_type",
        help="Gitlab resource type to sync with",
        type=str,
        choices=["project", "group"],
    )

    parser.add_argument(
        "gitlab_resource_id",
        help="Gitlab resource id to sync with",
        type=int,
    )

    parser.add_argument(
        dest="project_file",
        help="Microsoft Project File to sync with",
        type=str,
    )

    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    # we are not as complicated as that we need %(name)s:
    logformat = "[%(asctime)s] %(levelname)s: %(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def label_convert(label_string: str) -> str:
    """
    Convert the label string for easier matches
    """
    return label_string.lower().replace(" ", "")


def has_not_label(issue: Issue, label: str) -> bool:
    """
    Give true if to include the issue as it has no ignored label

    Args:
        issue: to compare with
        label: to ignore

    Returns: True if to include the label
    """
    if not label:
        return True
    for _label in issue.labels:
        if label_convert(_label) == label_convert(label):
            return False
    return True


def filter_by_labels(issues: List[Issue], label: str) -> List[Issue]:
    """
    Filter out issues whoes label matches given one

    Note: Currently not used as filtering is done directly in the match
          to allow better debug messages

    Args:
        issues: origin
        label: to filter out

    Returns: filtered list of issues
    """

    if not label:
        # Default for label is empty string, so in this case (or any other)
        # return the issues as they were
        return issues

    return list(filter(functools.partial(has_not_label, label=label), issues))


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    ms_project_file = Path(args.project_file)
    if not ms_project_file.is_file():
        _logger.error(
            f"Could not open '{args.project_file}' - seems not to be a valid file."
        )
        exit(128)
    _logger.debug("Starting loading issues")

    gitlab = get_gitlab_class(args.gitlab_url, args.gitlab_token)

    if args.gitlab_resource_type == "project":
        get_issues_func = get_project_issues
    elif args.gitlab_resource_type == "group":
        get_issues_func = get_group_issues
    else:
        raise ValueError("Invalid Resource Type")

    if args.fixed_work:
        sync_task_helper = ForceFixedWork
    else:
        sync_task_helper = SetTaskTypeConservative

    try:
        issues = get_issues_func(gitlab, args.gitlab_resource_id)
    except ConnectionError as e:
        _logger.error(f"Error contacting gitlab instance: {e}")
        exit(64)
    else:
        include_issue = functools.partial(has_not_label, label=args.ignore_label)
        with MSProject(ms_project_file.absolute()) as tasks:
            sync_gitlab_issues_to_ms_project(
                tasks, issues, WebURL(args.gitlab_url), sync_task_helper, include_issue
            )
    _logger.info("Finished syncing")


def run():
    """Entry point for console_scripts"""
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
