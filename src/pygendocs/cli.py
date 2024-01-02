"""Helper functionality for the pygendocs cli.
"""
from pathlib import Path
from typing import Iterable, List
from itertools import chain

from rich import print
from rich.status import Status

from .functions import get_functions_from_file, ResolvedFunction


def get_functions_from_paths(paths: List[Path]) -> List[ResolvedFunction]:
    with Status(f"Scanning input files...") as s:
        cleaned_paths = clean_input_paths(paths)

        return list(
            chain.from_iterable(get_functions_from_file(p) for p in cleaned_paths)
        )


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

    return cleaned_paths


def print_message(m: str):
    """Prints the given message `m` with some standard formatting."""
    print(f"  [bold yellow]>[/] [bold]{m}")
