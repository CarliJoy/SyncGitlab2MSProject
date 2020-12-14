from gitlab.v4.objects import GroupIssue, ProjectIssue
from typing import Any, Dict, NewType, Union

GitlabUserDict = Dict[str, Union[str, int]]
GitlabIssue = Union[GroupIssue, ProjectIssue]
IssueRef = NewType("IssueRef", int)
# Are Dynamic Types, therefore any
ComMSProjectProject = Any
ComMSProjectApplication = Any
WebURL = NewType("WebURL", str)
