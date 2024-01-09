"""Runnable task definitions for pyinvoke.

Use with `poetry run invoke <step>`.
Or from within a poetry shell, simply `invoke <step>`
"""
import sys

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
def formatting(c):
    _print_title("Checking code formatting")

    failed = False

    ### Check black
    _print_section("Black")
    try:
        c.run("poetry run black ./src --diff --check --color")
    except UnexpectedExit:
        _print_fail()
        failed = True

    if failed:
        sys.exit(1)


@task
def test(c):
    c.run("poetry run pytest src/tests/")


@task
def coverage(c):
    c.run("poetry run coverage run -m pytest ./src/tests/")