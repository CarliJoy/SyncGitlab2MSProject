from typing import List

from . import MSProject
from .gitlab_issues import Issue


def sync_gitlab_issues_to_ms_project(ms_project: MSProject, issues: List[Issue]):
    # Create Dictionary of all IDs to find moved ones and relate existing

    # Find moved issues and reference them
    pass
