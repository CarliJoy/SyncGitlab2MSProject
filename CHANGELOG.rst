=========
Changelog
=========

Version 0.0.7
=============
- Removed Notes
- Add ResourceNames from assignees
- Add Actual Start from gitlab created_at
- Add option for ignoring given project id within group
- Replaced Hyperlinkname with gitlab full reference
- Access Gitlab with ssl_verify set to false

Version 0.0.6
=============
- Add ``--ignore-label`` option :issue:`3`
- Add shortcuts ``-u`` and ``-t``  for gitlab url and gitlab token
- Add `PreCommit`_ to prevent failing builds :issue:`4`
- Fix Bug that percentage done was not calculated correctly :issue:`5`
- Syncing always set Task Type to Fixed Work but revert to original after sync :issue:`6`
- Adding parameter ``--force-fixed-work``  that does not reset the Task Type after sync
- Do not sync work with summary task :issue:`1`

Version 0.0.5
=============
- was only required to get travis to work, now it does!

Version 0.0.4
=============
- First auto release with travis
    - Use `Travis AWS`_
    - Use travis.com instead of travis.org

Version 0.0.3
=============
- Also use Hyperlink or Text29 URL field to find related issues
- Added documentation on how to fix the OpenURL Problem
- Fixed some sync bugs

Version 0.0.2
=============
- Documentation Only Changes
    - Add Badges
    - Import Readme to documentation
    - Allow build of documentation even without pywin32 installed
    - Use ReadTheDoc Sphinx Theme

Version 0.0.1
=============

- First Release

.. _Travis AWS: https://blog.travis-ci.com/2020-09-11-arm-on-aws
.. _PreCommit: https://pre-commit.com/
