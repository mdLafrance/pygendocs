"""Executable entrypoint for pygendocs
"""
import ast
import os
from itertools import chain
from pathlib import Path
from typing import Iterable, List, Tuple, Optional

import typer
from rich import print
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.status import Status

from . import llm
from .cli import clean_input_paths, print_message, get_functions_from_paths
from .config import read_from_toml
from .functions import ResolvedFunction, get_functions_from_file
from .git import check_for_git_changes

app = typer.Typer(add_completion=False)


@app.command(no_args_is_help=True)
def run(
    paths: List[Path], preview: bool = False, force: bool = False, test: bool = False
):
    """Automatically identifies and generates missing docstrings for python files
    using OpenAI (or the LLM of your choice)."""

    functions = get_functions_from_paths(paths)

    print("Running!")

    # fn = functions[0]

    # print("[bold yellow] > [/][bold]Generating docstring for:")
    # print(Panel(Syntax(fn.source_str, "python")))

    # client = llm.get_openai_client()

    # ds = llm.generate_function_docstring(client, fn)

    # print("Generated docstring:")
    # print(Panel(Syntax(ds, "python")))


@app.command()
def test():
    """Run a test scenario against the current LLM server configuration.

    Useful to check correctness if hosting your own LLM server, by making sure
    that the language model is behaving as expected.
    """
    print()
    print_message(f"Running test on current LLM configuration")
    print()


def preview_function_changes(functions: List[ResolvedFunction]):
    """Generates a preview for the docstrings that would be generated for `functions`."""

    print_message(f"Generating docstring previews")
    print()

    ### Filter out functions that have docstrings
    functions = [fn for fn in functions if not fn.has_docstring]

    ### Print the source code for each function
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
    print_message(
        f"The given docstrings would be applied to {len(functions)} functions across {num_files} files."
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


if __name__ == "__main__":
    app()
