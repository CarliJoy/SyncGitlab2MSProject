# -*- coding: utf-8 -*-
from pkg_resources import DistributionNotFound, get_distribution

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "SyncGitlab2MSProject"
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = "unknown"
finally:
    del get_distribution, DistributionNotFound

from .gitlab_issues import Issue
from .ms_project import MSProject
from .sync import sync_gitlab_issues_to_ms_project

__all__ = ["MSProject", "Issue", "sync_gitlab_issues_to_ms_project"]
