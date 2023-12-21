"""Functions for interacting with an LLM for code and comment generation.
"""
import ast
import os
from pathlib import Path

import openai
import tiktoken
from rich import print

# f = str((Path(__file__).parent / "./config.py").resolve())

# with open(f, 'r') as file:
#     nodes = ast.parse(file.read(), filename=f).body

#     fn = next(f for f in nodes if isinstance(f, ast.FunctionDef))

#     print(fn)
#     print(fn.body)
#     print(ast.unparse(fn.body[0]))
#     print(fn.body[0].lineno)


# p = """
# Generate and return only a docstring for this function in Google style

# def read_from_toml(config_file: str = "pyproject.toml") -> PyGenDocsConfiguration:
#     with open(config_file, 'r') as f:
#         config_dict = tomli.loads(f.read()).get("tool", {}).get("pygendocs", {})

#         return PyGenDocsConfiguration(**config_dict)
# """

# print(len(tiktoken.encoding_for_model("davinci").encode(p)))
