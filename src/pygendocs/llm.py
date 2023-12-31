"""Functions for interacting with an LLM for code and comment generation.
"""
import ast
import os
import logging

from functools import lru_cache
from pathlib import Path

import openai
import tiktoken

from rich import print

from .functions import ResolvedFunction


_LOGGER = logging.getLogger(__name__)


@lru_cache
def get_openai_client(base_url: str = None, api_key: str = None):
    """Generate an instance of an openai client to communicate with the llm server.

    This function will memoize results.

    Args:
        base_url: The web url the api server is reachable at.
        api_key: The api key used to authenticate with the server.

    Returns:
        An `openai.OpenAI` client object.
    """
    _LOGGER.debug(f"Generating llm client for {base_url} with key {api_key}")

    client = openai.OpenAI(base_url=base_url, api_key=api_key)

    _LOGGER.debug(f"Generated client: {client}")

    return client


def generate_function_docstring(client: openai.OpenAI, fn: ResolvedFunction) -> str:
    docstring = (
        client.completions.create(
            model="gpt2", prompt=_format_docstring_request_prompt(fn), max_tokens=800
        )
        .choices[0]
        .text
    )

    return docstring


def _format_docstring_request_prompt(fn: ResolvedFunction) -> str:
    return f"Generate a python docstring in Google style for the following function:\n\n{fn.source_str}"


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
