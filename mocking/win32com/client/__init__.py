# https://docs.microsoft.com/de-de/office/vba/api/project.pjsavetype
from typing import Iterable, Any

pjPromptSave = 2
pjSave = 1
pjDoNotSave = 0


class Task:
    def __getattribute__(self, item) -> Any:
        """A MS Task"""


class MSProject_Project:
    """Mocking Class for
    https://docs.microsoft.com/de-de/office/vba/api/project.project
    """

    @property
    def Path(self) -> str:
        """Path for the current file (folder)"""
        return ""

    @property
    def Name(self) -> str:
        """Name of the Project"""
        return "filename.mpp"

    @property
    def Tasks(self) -> Iterable[Task]:
        return []


class COMObject_MSProject_Application:
    """Mocking Class for MS Project Application COM Object
    https://docs.microsoft.com/de-de/office/vba/api/project.application
    """

    def FileOpen(self, path: str):
        """Open a project
        https://docs.microsoft.com/en-us/previous-versions/office/developer/office-2003/aa194681(v=office.11)
        """

    @property
    def ActiveProject(self) -> MSProject_Project:
        """Get Active Project
        https://docs.microsoft.com/de-de/office/vba/api/project.application.activeproject
        """
        return MSProject_Project()

    def Quit(self, save_changes: int = pjPromptSave) -> None:
        """
        Closes the application
        https://docs.microsoft.com/de-de/office/vba/api/project.application.quit
        """

    def FileSave(self) -> bool:
        """Save active project
        https://docs.microsoft.com/de-de/office/vba/api/project.application.filesave
        """

    def FileClose(self, Save: int = pjPromptSave, NoAuto: bool = True) -> None:
        """
        Close the active project
        https://docs.microsoft.com/en-us/previous-versions/office/developer/office-2003/aa194664(v=office.11)
        """

    @property
    def Projects(self) -> Iterable[MSProject_Project]:

        return []


def Dispatch(application: str) -> COMObject_MSProject_Application:
    """Create a COM connection"""
