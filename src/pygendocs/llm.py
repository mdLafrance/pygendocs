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

from cachier import cachier

from .config import LLMConfiguration
from .exceptions import APIKeyNotFoundError
from .functions import ResolvedFunction


_LOGGER = logging.getLogger(__name__)


@lru_cache
def get_llm_api_client(cfg: LLMConfiguration):
    """Generate an instance of an openai compatible client to communicate with the llm server.

    This function will cache repeated calls with the same configuration.

    Args:
        cfg: The current LLMConfiguration struct.

    Returns:
        An `openai.OpenAI` client object.
    """
    return openai.OpenAI(base_url=cfg.base_url, api_key=get_api_key(cfg))


def get_api_key(cfg: LLMConfiguration) -> str:
    """Get the api key required to communicate with the llm server.

    Args:
        cfg: The current LLMConfiguration struct.

    Returns:
        The appropriate api key.

    Raises:
        An `APIKeyNotFoundError` if the configured api key cannot be found in the environment.
    """
    try:
        return os.environ[cfg.api_token_env_key]
    except KeyError:
        raise APIKeyNotFoundError(
            f"API token cannot be found from environment key: {cfg.api_token_env_key}"
        )


@cachier()
def generate_function_docstring(function_body: str, cfg: LLMConfiguration) -> str:
    """Generate a function docstring for the given `function_body` according to
    the parameters outlined in the llm configuration struct `cfg`.

    Calls to this function are persistently cached with `cachier`.

    Args:
        function_body: The text data of a function to generate docstrings for.
        cfg: The current LLMConfiguration object.

    Returns:
        A newly generated docstring for the given function.
    """

    client = get_llm_api_client(cfg)

    return dispatch_completion(
        client, cfg, _format_docstring_request_prompt(function_body)
    )


def sanitize_docstring(fn: ResolvedFunction, docstring: str):
    if not docstring.endswith("\n"):
        docstring = docstring + "\n"

    return docstring


def dispatch_completion(
    client: openai.OpenAI, cfg: LLMConfiguration, message: str
) -> str:
    return (
        client.chat.completions.create(
            model=cfg.model,
            messages=[{"role": "user", "content": message}],
            max_tokens=cfg.max_tokens,
            n=1,
        )
        .choices[0]
        .message.content
    )


def generate_new_function_code_with_docstring(
    fn: ResolvedFunction, docstring: str
) -> str:
    print(fn)


def _format_docstring_request_prompt(function_body: str) -> str:
    return f"Generate a python docstring in Google style for the following function, only returning the docstring:\n\n{function_body}"
