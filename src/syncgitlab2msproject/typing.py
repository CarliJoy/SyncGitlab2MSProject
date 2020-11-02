from typing import Union, Dict

from gitlab.v4.objects import ProjectIssue, GroupIssue

GitlabUserDict = Dict[str, Union[str, int]]
GitlabIssue = Union[GroupIssue, ProjectIssue]
