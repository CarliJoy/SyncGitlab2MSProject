class GitlabSyncError(ValueError):
    pass


class MovedIssueNotDefined(GitlabSyncError):
    pass


class MSProjectSyncError(ValueError):
    pass


class LoadingError(MSProjectSyncError):
    pass


class ClassNotInitiated(MSProjectSyncError):
    """Tried to load a function without properly initiate the class"""
