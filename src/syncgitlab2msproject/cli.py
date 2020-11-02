# -*- coding: utf-8 -*-
"""
Handle the Command Line Interface
"""

import argparse
import sys
import logging

from syncgitlab2msproject import __version__

__author__ = "Carli Freudenberg"
__copyright__ = "Carli Freudenberg"
__license__ = "mit"

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
        help="URL to the gitlab instance i.e. https://gitlab.your-company.com",
        default="https://gitlab.com",
        type=str,
    )

    # TODO read from ENV
    parser.add_argument(
        "--gitlab-token",
        help="Gitlab personal access token",
    )

    parser.add_argument(
        "gitlab-resource-type",
        help="Gitlab resource type to sync with",
        type=str,
        choices=["project", "group"],
    )

    parser.add_argument(
        "gitlab-resource-id",
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
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
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
    _logger.debug("Starting crazy calculations...")

    # print("The {}-th Fibonacci number is {}".format(args.n, fib(args.n)))
    _logger.info("Script ends here")


def run():
    """Entry point for console_scripts"""
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
