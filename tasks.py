"""Runnable task definitions for pyinvoke.

Use with `poetry run invoke <step>`.
Or from within a poetry shell, simply `invoke <step>`
"""

from invoke import task
from invoke.exceptions import UnexpectedExit

from rich import print
from rich.rule import Rule


def _print_title(*m):
    print(Rule(str(*m)))

def _print_section(*m):
    print("[bold blue]>>>[bold]", *m, "\n")

def _print_fail():
    print("[bold red]\nFAILED\n")


@task
def build(c):
    _print_title("Building package")

    c.run("poetry build")


@task
def format(c):
    _print_title("Formatting code")

    c.run("poetry run black ./src")


@task 
def check_formatting(c):
    _print_title("Checking code formatting")

    ### Check black
    _print_section("Black")
    try:
        c.run("poetry run black ./src --diff --check --color")
    except UnexpectedExit:
        _print_fail()


    ### Check import orders are orderly
    _print_section("Isort (import sort)")
    try:
        c.run("poetry run isort ./src --check")
    except UnexpectedExit:
        _print_fail()


@task
def test(c):
    c.run("poetry run pytest src/tests/")