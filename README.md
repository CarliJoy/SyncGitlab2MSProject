[![Build Status](https://travis-ci.com/CarliJoy/SyncGitlab2MSProject.svg?branch=master&status=created)](https://travis-ci.com/CarliJoy/SyncGitlab2MSProject)
[![PyPi Version](https://img.shields.io/pypi/v/SyncGitlab2MSProject.svg)](https://pypi.org/project/SyncGitlab2MSProject/)
[![PyPi Downloads](https://img.shields.io/pypi/dm/SyncGitlab2MSProject.svg?maxAge=2592000?style=plastic)](https://pypistats.org/packages/syncgitlab2msproject)
[![Python Versions](https://img.shields.io/pypi/pyversions/SyncGitlab2MSProject.svg)](https://pypi.org/project/SyncGitlab2MSProject/)
[![Wheel Build](https://img.shields.io/pypi/wheel/SyncGitlab2MSProject.svg)](https://pypi.org/project/SyncGitlab2MSProject/)
[![Project Status](https://img.shields.io/pypi/status/SyncGitlab2MSProject.svg)](https://pypi.org/project/SyncGitlab2MSProject/)
[![Code Style Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/syncgitlab2msproject/badge/?version=latest)](https://syncgitlab2msproject.readthedocs.io/en/latest/?badge=latest)
[![Average time to resolve an issue](http://isitmaintained.com/badge/resolution/CarliJoy/SyncGitlab2MSProject.svg)](http://isitmaintained.com/project/CarliJoy/SyncGitlab2MSProject)
[![Percentage of issues still open](http://isitmaintained.com/badge/open/CarliJoy/SyncGitlab2MSProject.svg)](http://isitmaintained.com/project/CarliJoy/SyncGitlab2MSProject)

# Help wanted

I don't own Microsoft Project anymore. So if there is anybody willing to take up the development/maintance, just open an issue.

# SyncGitlab2MSProject

Sync Gitlab Issues into a Microsoft Project File.
Use it if you use MS Project for the general project planning but want to keep
the Issues in Gitlab as a part of your project planning to follow the process progess.

Currently only Information from Gitlab Issues are inserted and updated within the
Project File. Changes in synchronised fields will be overwritten.

The following MS Project attributes are synced (overwritten) from gitlab:
  - Name (from title)
  - Notes (from description) removed
  - Deadline (from due_date)
  - Work (from time_estimate)
  - Actual Work (from total_time_spent)
  - Actual Start (from created_at)
  - Actual Finish (from closed_at)
  - Percent Complete (if Tasks given for issue, otherwise only 0% and 100% [for closed])
  - Text28 (list of labels)
  - Text29 (URL to gitlab issue)
  - Text30 (the reference to the issue is stored there)
  - Hyperlink (link/URL to gitlab issue)
  - ResourceNames (from Assigned)

Moved issues will be handled if the group selected and the issue was moved within the
group. Problem is that accessing issues only by ID is just allowed for admins.

## Requirements
This project runs only in an Windows Environment with Microsoft Project installed.

**Please note:** This Script has been tested only mit Microsoft Project 2016.
It could be, that some of the API has changed in newer versions.
If you run into any troubles with a new version, please open an
[Issue](https://github.com/CarliJoy/SyncGitlab2MSProject/issues/new).

## Usage
```
usage: sync_gitlab2msproject [-h] [--version] [-v] [-vv] [--gitlab-url GITLAB_URL] [--gitlab-token GITLAB_TOKEN] {project,group} gitlab_resource_id project_file

Sync Gitlab Issue into MS Project

positional arguments:
  {project,group}       Gitlab resource type to sync with
  gitlab_resource_id    Gitlab resource id to sync with
  project_file          Microsoft Project File to sync with

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -v, --verbose         set loglevel to INFO
  -vv, --very-verbose   set loglevel to DEBUG
  --gitlab-url GITLAB_URL
                        URL to the gitlab instance i.e. https://gitlab.your-company.com
  --gitlab-token GITLAB_TOKEN
                        Gitlab personal access token

```

## Quickstart
1. Optional: Install [pipx](https://github.com/pipxproject/pipx)
2. Install the package `pipx install SyncGitlab2MSProject` (or use `pip` if you don't like pipx)
3. Push the gitlab Issue to your MS Project file:
`sync_gitlab2msproject --gitlab-url https://gitlab.company.com --gitlab-token <your_token> group <your_group_id> ms_project_file.mpp`

## Open Hyplerlink Problems
If you have troubles that the wrong issues are opened once you click on a Hyperlink use
the following VBA Script as a workaround.
Simply add the VBA script to your Ribbon and it will open all Hyperlinks of the
selected tasks.

```vbscript
Option Explicit

Private Declare Function ShellExecute _
  Lib "shell32.dll" Alias "ShellExecuteA" ( _
  ByVal hWnd As Long, _
  ByVal Operation As String, _
  ByVal Filename As String, _
  Optional ByVal Parameters As String, _
  Optional ByVal Directory As String, _
  Optional ByVal WindowStyle As Long = vbMinimizedFocus _
  ) As Long

Public Sub OpenUrls()

    Dim lSuccess As Long
    Dim T As Task
    Dim Names As String
    For Each T In ActiveSelection.Tasks
        lSuccess = ShellExecute(0, "Open", T.HyperlinkAddress)
    Next T
End Sub

```

## Note

This project has been set up using PyScaffold 3.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.
