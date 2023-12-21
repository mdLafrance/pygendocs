"""Functionality to parse user defined config variables.
"""

from enum import Enum

import tomli
from pydantic import BaseModel


class DocstringStyle(str, Enum):
    reST = "reST"
    Google = "Google"
    Epytext = "Epytext"
    Numpydoc = "Numpydoc"


class PyGenDocsConfiguration(BaseModel):
    """
    Data struct encoding configuration options for PyGenDocs.

    This class should be considered the 'source of truth' with regards to supported
    syntax and options in pyproject.toml.
    """

    ignore_internal: bool = False
    """Whether or not to ignore objects and functions beginning with an underscore."""

    ignore_private: bool = True
    """Whether or not to ignore objects and functions beginning with a double underscore."""

    include_fixme_header: bool = True
    """Whether or not to prepend an additional line of documentation containing a TOTO: 
    tag signalling that this docstring was autogenerated and should be reviewed."""

    exclude_constructors: bool = True
    """Whether or not to ignore class constructor __init__ functions. Defaults to True."""

    docstring_style: DocstringStyle = DocstringStyle.Google
    """The style with which the generated docstring should be written. 
    
    Defaults to Google python style.
    """

    openai_api_env_key: str = "PYGENDOCS_OPENAI_API_KEY"
    """The environment key from which your openai api token will be read."""

    openai_endpoint_env_key: str = None
    """The environment key from which an override to the default openai api
    endpoint can be specified.
    
    For example, if locally hosting an LLM which implements the openai protocol."""

    class config:
        allow_arbitrary_types = True


def read_from_toml(config_file: str = "pyproject.toml") -> PyGenDocsConfiguration:
    ...
    # a = 10
    # with open(config_file, 'r') as f:
    #     config_dict = tomli.loads(f.read()).get("tool", {}).get("pygendocs", {})

    #     return PyGenDocsConfiguration(**config_dict)
