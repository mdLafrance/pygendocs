"""Helper functionality for the pygendocs cli.
"""
from pathlib import Path
from typing import Iterable, List


def clean_input_paths(paths: List[Path]) -> List[Path]:
    """Sorts and removes duplicates from the given paths."""
    return sorted(list(set(flatten_input_paths(list(p.resolve() for p in paths)))))


def flatten_input_paths(paths: Iterable[Path]) -> List[Path]:
    """Expands and flattens input directories and files to conatin all descendent files."""
    cleaned_paths = []

    for p in paths:
        if p.is_dir():
            cleaned_paths.extend(flatten_input_paths(p.glob("*")))

        elif p.is_file() and p.suffix == ".py":
            cleaned_paths.append(p)

        else:
            raise RuntimeError(f"Unknown filesystem object: {p}")

    return cleaned_paths
