# -*- coding: utf-8 -*-
from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "SyncGitlab2MSProject"
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = "unknown"
finally:
    del get_distribution, DistributionNotFound

from .ms_project import MSProject
from .gitlab_issues import Issue
from .sync import sync_gitlab_issues_to_ms_project

__all__ = ["MSProject", "Issue", "sync_gitlab_issues_to_ms_project"]
