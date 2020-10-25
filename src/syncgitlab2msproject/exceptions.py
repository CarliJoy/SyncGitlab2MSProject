class MSProjectSyncError(ValueError):
    pass


class LoadingError(MSProjectSyncError):
    pass

class ClassNotInitiated(MSProjectSyncError):
    """Tried to load a function without properly initiate the class"""

