"""Helper functionality for the pygendocs cli.

These functions should only be called directly from the cli, as some of them 
will call sys.exit() on a fail state.
"""
import os
import re
import sys

from pathlib import Path
from typing import Iterable, List
from itertools import chain

from rich import print
from rich.status import Status
from rich.panel import Panel
from rich.syntax import Syntax

from .config import PyGenDocsConfiguration
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


def filter_functions(
    functions: List[ResolvedFunction], cfg: PyGenDocsConfiguration
) -> List[ResolvedFunction]:
    """Filter out functions based on the given configuration.

    For example, the configuration can specify to ignore class constructors,
    private functions, and protected functions.

    Return a subset of `functions` that adheres to the config.
    """
    ### Filter for functions which already have docstrings
    res = [f for f in functions if not f.has_docstring]

    ### Filter constructors
    if cfg.ignore_constructors:
        res = [f for f in res if not f.name == "__init__"]

    ### Filter internal
    if cfg.ignore_internal:
        res = [f for f in res if not re.match("^_[^_]+", f.name)]

    ### Filter private
    if cfg.ignore_private:
        res = [f for f in res if not re.match("^__[^_]+", f.name)]

    return res


def try_get_api_key(api_env_key: str) -> str:
    """Try and get the api key from the given environment variable `api_env_key`.

    Will print a message and exit on fail.
    """
    try:
        return os.environ[api_env_key]

    except KeyError:
        print_error(
            f"API token cannot be found from environment key [bold]'{api_env_key}'"
        )
        sys.exit(1)


def print_message(m: str):
    """Prints the given message `m` with some standard formatting."""
    print(f"  [bold yellow]>[/] [bold]{m}")


def print_error(m: str):
    print(f"  [bold red]ERROR: [/]{m}")


def print_chat_message(title: str, message: str):
    print(Panel(message, title=title, title_align="left", padding=1))


def print_function(fn: ResolvedFunction, lines: int = 50):
    # Truncate the function body string to `lines`.
    body = "\n".join(fn.source_str.split("\n")[:lines])

    print(
        Panel(
            Syntax("\n" + body, "python"),
            title=f"{fn.source_file}:[bold]{fn.name}",
            title_align="left",
        )
    )


def update_config(cfg: PyGenDocsConfiguration, opts: dict) -> PyGenDocsConfiguration:
    return PyGenDocsConfiguration(**dict(cfg.model_dump(), **opts))
