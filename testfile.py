import os

import sys

import tomli

from rich import print

SOME_CONST = 1234

def read_from_toml(
        config_file: str = "pyproject.toml"
) -> dict:
    a = 10
    with open(config_file, 'r') as f:
        config_dict = tomli.loads(f.read()).get("tool", {}).get("pygendocs", {})

        return config_dict


class Foo:
    """Some foo class"""

    def __init__(self):
        pass


    def methodA(self):
        return 10


    def methodB(self, config_file):
        """alksdjflajsd"""
        with open(config_file, 'r') as f:
            config_dict = tomli.loads(f.read()).get("tool", {}).get("pygendocs", {})

        self.config_dict = config_dict

        return config_dict