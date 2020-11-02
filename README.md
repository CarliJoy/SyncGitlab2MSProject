# SyncGitlab2MSProject

Sync Gitlab Issues with a Microsoft Project File.
Use it if you use MS Project for the general project planning but want to keep
the Issues in Gitlab as a part of project planning to follow the process.

Currently only Information from Gitlab Issues are inserted and updated within the
Project File. Changes in synchronised fields will be overwritten.

The following MS Project attributes are synched from gitlab:
  - Name
  - Notes (from Description)
  - Deadline (from Due Date)

Not yet implemented but planned
  - ...

## Requirements
This project runs only in an Windows Environment with Microsoft Project installed.

## Note

This project has been set up using PyScaffold 3.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.
