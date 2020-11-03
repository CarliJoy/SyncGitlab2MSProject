from typing import Union, Dict, NewType

from gitlab.v4.objects import ProjectIssue, GroupIssue

GitlabUserDict = Dict[str, Union[str, int]]
GitlabIssue = Union[GroupIssue, ProjectIssue]
IssueRef = NewType('IssueRef', int)