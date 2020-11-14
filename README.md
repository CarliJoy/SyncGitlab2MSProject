# SyncGitlab2MSProject

Sync Gitlab Issues with a Microsoft Project File.
Use it if you use MS Project for the general project planning but want to keep
the Issues in Gitlab as a part of project planning to follow the process.

Currently only Information from Gitlab Issues are inserted and updated within the
Project File. Changes in synchronised fields will be overwritten.

The following MS Project attributes are synced (overwritten) from gitlab:
  - Name
  - Notes (from Description)
  - Deadline (from Due Date)
  - Work (from Time Estimated)
  - Actual Work (from Time Spent)
  - Percent Complete (if Tasks given for issue, otherwise only 0% and 100% [for closed])
  - Text28 (the list of label)
  - Text30 (the reference to the issue is stored there)
  - Hyperlink (link to gitlab issue - note: somehow ms project is not handling the links correctly) 

Not yet implemented but planned:
  - Resources (from Assigned)

Moved issues will be handled if the group selected and the issue was moved within the 
group. Problem is that accessing issues only by ID is just allowed for admins.
## Requirements
This project runs only in an Windows Environment with Microsoft Project installed.

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

## Note

This project has been set up using PyScaffold 3.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.
