"""Miscellaneous functionality not specific to a single problem space.
"""

from git import Repo

def check_for_git_changes() -> bool:
    repo = Repo('.')

    print(f"Unstaged/uncommited changes: {repo.is_dirty()}")
    print(f"Untracked files: {len(repo.untracked_files)}")
