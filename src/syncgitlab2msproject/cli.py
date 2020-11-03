# -*- coding: utf-8 -*-
"""
Handle the Command Line Interface
"""

import argparse
import sys
import logging
from pathlib import Path

from requests import ConnectionError
from syncgitlab2msproject import __version__, MSProject

__author__ = "Carli Freudenberg"
__copyright__ = "Carli Freudenberg"
__license__ = "mit"

from syncgitlab2msproject.gitlab_issues import get_project_issues, get_gitlab_class, get_group_issues
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

    # TODO read from ENV
    parser.add_argument(
        "--gitlab-url",
        dest="gitlab_url",
        help="URL to the gitlab instance i.e. https://gitlab.your-company.com",
        default="https://gitlab.com",
        type=str,
    )

    # TODO read from ENV
    parser.add_argument(
        "--gitlab-token",
        dest="gitlab_token",
        help="Gitlab personal access token",
        default=None
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

    try:
        issues = get_issues_func(gitlab, args.gitlab_resource_id)
    except ConnectionError as e:
        _logger.error(f"Error contacting gitlab instance: {e}")
        exit(64)
    else:
        with MSProject(ms_project_file.absolute()) as tasks:
            sync_gitlab_issues_to_ms_project(tasks, issues)
    _logger.info("Finished syncing")


def run():
    """Entry point for console_scripts"""
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
