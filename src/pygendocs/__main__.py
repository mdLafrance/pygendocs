"""Executable entrypoint for pygendocs
"""
import ast
import os
import sys

from itertools import chain
from pathlib import Path
from typing import Iterable, List, Tuple, Optional
from typing_extensions import Annotated
from dataclasses import dataclass

import typer
from rich import print, box
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.status import Status
from rich.markup import escape
from rich.prompt import Prompt

from . import llm
from .llm import get_llm_api_client, dispatch_completion, generate_function_docstring
from .cli import (
    clean_input_paths,
    print_message,
    get_functions_from_paths,
    try_get_api_key,
    filter_functions,
    print_function,
    get_updated_config,
    format_function_location,
    answered_yes
)
from .config import read_from_toml
from .functions import ResolvedFunction, get_functions_from_file, write_new_docstring
from .git import repo_has_changes, is_git_repo


app = typer.Typer(add_completion=False, no_args_is_help=True)

_CFG = read_from_toml()


@dataclass
class CommonArgs:
    Paths: List[Path] = typer.Argument(
        None,
        help="Input paths to scan for functions. Can be a combination of directories and files. Directories will be recursed into.",
    )
    IgnoreConstructors: bool = typer.Option(
        _CFG.ignore_constructors, help="Ignore class constructor functions."
    )
    IgnorePrivate: bool = typer.Option(
        _CFG.ignore_private,
        help="Ignore private functions. Private functions have two leading underscores.",
    )
    IgnoreInternal: bool = typer.Option(
        _CFG.ignore_internal,
        help="Ignore internal functions. Internal functions have one leading underscore.",
    )


@app.command()
def run(
    paths: List[Path] = CommonArgs.Paths,
    ignore_constructors: bool = CommonArgs.IgnoreConstructors,
    ignore_private: bool = CommonArgs.IgnorePrivate,
    ignore_internal: bool = CommonArgs.IgnoreInternal,
    force: bool = typer.Option(False, help="Ignore git safety checks.")
):
    """Automatically identifies and generates missing docstrings for python files
    using OpenAI (or the LLM of your choice)."""

    ### Check that the current running environment is in a clean git repo
    if not force:
        suggestion_message = "[/]NLP code generation can deliver mixed results, so it is recommended that modified files exist in version tracking so changes can be reverted.  [dim]Override with --force."

        if not is_git_repo():
            print()
            print_message("[bold yellow]WARNING: [/]The current directory is not part of a git repository.")
            print_message(suggestion_message)
            print()
            sys.exit(1)

        if repo_has_changes():
            print()
            print_message("[bold yellow]WARNING: [/]The current git repo has pending changes.")
            print_message(suggestion_message)
            print()
            sys.exit(1)

    ### Update config with command line opts
    cfg = get_updated_config(
        {
            "ignore_internal": ignore_internal,
            "ignore_private": ignore_private,
            "ignore_constructors": ignore_constructors,
        },
    )

    ### Scan for functions to modify
    functions = filter_functions(get_functions_from_paths(paths), cfg)

    # NOTE: Preprocessing step to sort functions by reverse-appearence in file.
    #       This is so that when writing new lines into the file, we insert
    #       upwards from the bottom as to not corrupt existing line numbers we
    #       have scanned.
    functions = sorted(functions, key=lambda fn: (fn.source_file, fn.ast_object.lineno), reverse=True)

    if not functions:
        print()
        print_message("No functions to modify!")
        print()
        sys.exit(0)

    else:
        print()
        print("[bold]The following functions are missing docstrings:")

        for fn in functions:
            print(" -", f"{fn.source_file}:[bold]{fn.name}")

    print()
    if not answered_yes("Generate docstrings for these functions?"):
        sys.exit(0)

    ### Dispatch docstring gen
    generated_docstrings = {}
    """Mapping from collected function objects to their newly generated docstrings"""

    for fn in functions:
        with Status(f"Generating docstring for {fn.name}"):
            generated_docstrings[fn] = generate_function_docstring(fn.source_str, cfg.llm_configuration)

    print()
    print_message("The following docstrings were generated:")
    print()

    for fn, docstring in generated_docstrings.items():
        print(Panel(Syntax(docstring, "python"), title=f"{format_function_location(fn)}", title_align="left"))

    print()
    if not answered_yes("Apply changes?"):
        sys.exit(0)

    print()

    for fn, docstring in generated_docstrings.items():
        with Status(f"Writing docstring for {fn.name}..."):
            write_new_docstring(fn, docstring)

        print(f"✅ Wrote new docstring for {format_function_location(fn)} ")

    print()
        

@app.command()
def check(
    paths: List[Path] = CommonArgs.Paths,
    coverage: float = typer.Option(
        100, help="Coverage threshold of docstrings to fail under."
    ),
    ignore_internal: bool = CommonArgs.IgnoreInternal,
    ignore_private: bool = CommonArgs.IgnorePrivate,
    ignore_constructors: bool = CommonArgs.IgnoreConstructors,
):
    """Scans the given input paths for functions that are missing docstrings.

    This command will exit 1 if the given coverage of docstrings in specified
    functions is below the given threshold.

    Coverage threshold, and which types of functions to check can be configured in the command
    line or in your `pyproject.toml`file.
    """
    ### Update config with command line options
    cfg = get_updated_config(
        {
            "ignore_internal": ignore_internal,
            "ignore_private": ignore_private,
            "ignore_constructors": ignore_constructors,
            "coverage_threshold": coverage,
        },
    )

    ### Parse input files
    all_functions = get_functions_from_paths(paths)
    functions = filter_functions(all_functions, cfg)

    ### Print the source code for each function
    if functions:
        print()
        print_message(
            f"The following {len(functions)} functions are missing docstrings:"
        )
        print()

        for fn in functions:
            print_function(fn)

        print()

    ### Calculate coverage and report
    cov = 100 - (float(len(functions)) * 100 / len(all_functions))

    if cov >= coverage:
        print()
        print_message(
            f"[green bold]{cov:.2f}%[/] of functions have docstrings. [dim](Threshold {coverage}%)"
        )
        print()
    else:
        print_message(
            f"Only [bold red]{cov:.2f}%[/] of functions have docstrings. [dim](Threshold {coverage}%)"
        )
        print()
        sys.exit(1)


@app.command()
def test(message: Annotated[Optional[str], typer.Argument()] = None):
    """Run a test scenario against the current LLM server configuration.

    Useful to check correctness if hosting your own LLM server, by making sure
    that the language model is behaving as expected.

    Pass a message surrounded by quotes, which the configured LLM will respond to.
    """
    ### Fetch config data
    config = read_from_toml()
    api_key = try_get_api_key(config.llm_api_token_env_key)

    print()
    print_message(f"Running test on current LLM configuration:")

    ### Print current config in a table
    t = Table("URL", "Model", "Max Tokens", box=box.SIMPLE_HEAD)
    t.add_row(
        config.llm_api_url or "DEFAULT",
        config.llm_model,
        str(config.llm_completion_max_tokens),
    )

    print(t)

    ### Ping llm server
    message = message or "Say hello!"

    print(Panel(message, title=f"🙋", title_align="left", padding=1))

    client = get_llm_api_client(config.llm_api_url, api_key)

    resp = dispatch_completion(
        client, config.llm_configuration, message or "Say hello!"
    )

    print(Panel(resp, title=f"🤖 ({config.llm_model}):", title_align="left", padding=1))


if __name__ == "__main__":
    app()
