"""Executable entrypoint for pygendocs
"""

import typer

from .config import read_from_toml
from .git import check_for_git_changes


app = typer.Typer(add_completion=False)


@app.command()
def main(check: bool = False):
    """Automatically identifies and generates missing docstrings for python files
    using OpenAI (or the LLM of your choice)."""
    print("foo!")


if __name__ == "__main__":
    app() 