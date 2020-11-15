from typing import Union, Dict, NewType, Any

from gitlab.v4.objects import ProjectIssue, GroupIssue

GitlabUserDict = Dict[str, Union[str, int]]
GitlabIssue = Union[GroupIssue, ProjectIssue]
IssueRef = NewType("IssueRef", int)
# Are Dynamic Types, therefore any
ComMSProjectProject = Any
ComMSProjectApplication = Any
