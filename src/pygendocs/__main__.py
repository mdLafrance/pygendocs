"""Executable entrypoint for pygendocs
"""
import ast
import os
from itertools import chain
from pathlib import Path
from typing import Iterable, List, Tuple

import typer
from rich import print
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from . import llm
from .config import read_from_toml
from .functions import ResolvedFunction, get_functions_from_file
from .git import check_for_git_changes

app = typer.Typer(add_completion=False)


@app.command()
def main(paths: List[Path], preview: bool = False, force: bool = False):
    """Automatically identifies and generates missing docstrings for python files
    using OpenAI (or the LLM of your choice)."""

    cleaned_paths = sorted(list(set(_resolve_paths(list(p.resolve() for p in paths)))))

    functions = list(
        chain.from_iterable(get_functions_from_file(p) for p in cleaned_paths)
    )

    if preview:
        preview_function_changes(functions)

    fn = functions[0]

    print("[bold yellow] > [/][bold]Generating docstring for:")
    print(Panel(Syntax(fn.source_str, "python")))

    client = llm.get_openai_client()

    ds = llm.generate_function_docstring(client, fn)

    print("Generated docstring:")
    print(Panel(Syntax(ds, "python")))


def preview_function_changes(functions: List[ResolvedFunction]):
    ### Filter out functions that have docstrings
    functions = [fn for fn in functions if not fn.has_docstring]

    ### Print the source code for each function

    print()
    print(f"  [bold yellow]> [/][bold]Generating docstring preview")

    for fn in functions:
        print(
            Panel(
                Syntax("\n" + fn.source_str, "python"),
                title=f"{fn.source_file}:[bold]{fn.name}",
                title_align="left",
            )
        )

    ### Format some output
    num_files = len(set(fn.source_file for fn in functions))

    print()
    print(
        f"  [bold yellow]> [/][bold]The given docstrings would be applied to {len(functions)} functions across {num_files} files."
    )
    print()


def generate_functions_table(functions: List[ResolvedFunction]) -> str:
    t = Table()

    t.add_column("Source file")
    t.add_column("Function name")

    for fn in functions:
        if not fn.has_docstring:
            t.add_row(fn.source_file, fn.name)

    return t


def _resolve_paths(paths: Iterable[Path]) -> List[Path]:
    cleaned_paths = []

    for p in paths:
        if p.is_dir():
            cleaned_paths.extend(_resolve_paths(p.glob("*")))

        elif p.suffix == ".py":
            cleaned_paths.append(p)

    return cleaned_paths


if __name__ == "__main__":
    app()
