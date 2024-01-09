"""Functionality for interacting with git.

This is used to make sure the user has the running directory in version control,
and that there are no pending changes hanging.

This is due to the fact that pygendocs will modify the code with potentially 
unreliable code generated from an LLM, and we want to be able to roll back any 
potentially inaccurate results that were generated.

NOTE: This uses the PyGit library which imports as 'git'. Be sure to import this 
function as .git or with a full import path to avoid a collision.
"""

from git import Repo
from git.exc import InvalidGitRepositoryError


def is_git_repo() -> bool:
    try:
        Repo(".")
        return True
    except InvalidGitRepositoryError:
        return False


def repo_has_changes() -> bool:
    repo = Repo(".")

    return bool(repo.is_dirty() or repo.untracked_files)
