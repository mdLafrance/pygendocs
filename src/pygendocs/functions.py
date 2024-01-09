"""Functionality for identifying and modifying docstrings in functions.
"""

import ast
import logging

from pathlib import Path
from typing import List, Union
from textwrap import indent

from pydantic import BaseModel

from .config import PyGenDocsConfiguration

_LOGGER = logging.getLogger(__name__)


class ResolvedFunction(BaseModel):
    """`ResolvedFunction` dataclass contains meta information about a funcion
    that has been extracted from a source file for the purposes of modification."""

    name: str
    """The function name,"""

    source_file: str
    """Source file this function originates from."""

    source_str: str
    """Actual string data of this function."""

    has_docstring: bool
    """Whether or not this function has a docstring."""

    ast_object: ast.FunctionDef
    """Reference to the `ast.FunctionDef` object describing this function."""

    class Config:
        arbitrary_types_allowed = True

    def __hash__(self):
        return hash(f"{self.source_file}:{self.name}")


def docstring_lineno(fn: ast.FunctionDef) -> int:
    """Determines the appropriate line number a function docstring should be
    inserted at. If a docstring already exists, the line number of the docstring is returned.
    """

    if ast.get_docstring(fn):
        # NOTE: Docstrings are the first element of the function body.
        return fn.body[0].lineno

    else:
        # NOTE: Case where no docstring exists. Step one line back from the first
        # definition in the function. This is to handle formatted function definitions
        # which span multiple lines, in which adding the docstring simply following
        # the function declaration line would insert in the middle of the function prototype.
        return fn.body[0].lineno - 1


def get_functions_from_file(file: str | Path) -> List[ResolvedFunction]:
    """Extract all function definitions from the given `file` as encoded by
    their `ast.FunctionDef` representations.

    Function structs are sorted by function name.
    """
    file = str(file)

    with open(file, "r") as f:
        src = f.read()

    nodes = ast.parse(src, filename=file).body

    ### Recursively collect all function definitions from the file
    all_nodes = []

    for n in nodes:
        all_nodes.extend(ast.walk(n))

    ### Create a `ResolvedFunction` object for each function
    function_structs = []

    for fn in (n for n in all_nodes if isinstance(n, ast.FunctionDef)):
        function_structs.append(
            ResolvedFunction(
                name=fn.name,
                source_file=file,
                source_str=ast.get_source_segment(src, fn),
                ast_object=fn,
                has_docstring=ast.get_docstring(fn) is not None,
            )
        )

    return sorted(function_structs, key=lambda fn: fn.name)


def sanitize_docstring(fn: ResolvedFunction, docstring: str):
    ### Append trailing newline if not present
    if not docstring.endswith("\n"):
        docstring = docstring + "\n"

    ### Indent docstring body
    docstring = indent(docstring, " " * fn.ast_object.body[0].col_offset)

    return docstring


def write_new_docstring(fn: ResolvedFunction, docstring: str):
    """Write the new `docstring` for the given function `fn`."""

    with open(fn.source_file, 'r') as f:
        file = f.readlines()
        
    file.insert(docstring_lineno(fn.ast_object), sanitize_docstring(fn, docstring))

    with open(fn.source_file, 'w') as f:
        f.writelines(file)


def _dump_function_information(fn: ast.FunctionDef) -> str:
    """Returns a string representation of an `ast.FunctionDef` object, with
    several items exposed for better visibility when debugging."""
    return f"Function <{fn.name}> lines [{fn.lineno}, {fn.end_lineno}] with offset {fn.col_offset}"
