> [!IMPORTANT]
> ⚠️ 👷‍♂️ Still in development ⚠️

<h1 align=center>
  
  **pygendocs**
  
</h1>



<h3 align=center>
  
⚡ 🤖 ⚡

</h3>

<div align=center>

  [![Pipeline](https://github.com/mdLafrance/pygendocs/actions/workflows/pipeline.yml/badge.svg)](https://github.com/mdLafrance/pygendocs/actions/workflows/pipeline.yml)
  [![PyPI version](https://badge.fury.io/py/pygendocs.svg)](https://badge.fury.io/py/pygendocs)
  [![Coverage Status](https://coveralls.io/repos/github/mdLafrance/pygendocs/badge.svg?branch=update/base-functionality)](https://coveralls.io/github/mdLafrance/pygendocs?branch=update/base-functionality)
  
</div>

<h3 align=center>

  Generates documentation for python 🐍 functions in-place using LLMs 

</h3>

## About

`pygendocs` scans your source code for functions that are missing docstrings, and can generate and insert them directly into the file.

- Options can be configured through command line flags, or in your project's `pyproject.toml` 🛠️
- Can be used to check docstring coverage on your project and in CI
- Changes can first be previewed 👀
- Changes will not be applied unless you are on a clean git branch ✔️
- The api endpoint used for doc generation can be configured to use a self-hosted LLM 🤖

## Installation 🌎

`pygendocs` can be installed using `pip`, but [pipx](https://github.com/pypa/pipx) is recommended:

```bash
pipx install pygendocs
```

The `pygendocs` shell script should then be available in your terminal:

```bash
pygendocs --help
```

<br />

Out of the box, `pygendocs` is set up to use [gpt-4](https://platform.openai.com/docs/api-reference), which requires a subscription to their api service.  
If you don't feel like giving your money to skynet, or are just curious, see the section on self-hosting an llm server [here](asdf).

## Usage 🐍
Use the `pygendocs` command line tool to insert missing docstrings into your source code. One or more paths to files or directories can be supplied:
```bash
pygendocs run ./src
```
This will:
- Scan the given directory `src` for python files, and within those files, for functions that don't have docstrings
- Dispatch calls to the configured LLM server to generate docstrings
- Write them into the source code

Since NLP code generation can deliver mixed results, `pygendocs` will won't make changes if it detects that the current git branch is dirty, or there is no git branch present. This can be overriden with `--force`.

Most behaviours can be overriden or modified through the command line. Run 
```bash
pygendocs --help
```
to see the complete list of options.

### Previewing changes
If you just want some inspiration, or want to test what will happen, running the `preivew` subcommand will not write any changes, and instead display the generated docstrings in the terminal.

### Checking docstring coverage
You can use the `coverage` subcommand to get a summary of which functions in the given source are missing docstsrings, and what the coverage % of docstrings is.
This process will exit with returncode `1` if the coverage threshold was not reached.

Coverage threshold can be configured with the `--coverage` flag, or in `pyproject.toml`.

## Configuration ⚙️
Persistent configuration for `pygendocs` can be written in your project's `pyproject.toml` folder, in the subsection:
```toml
[tool.pygendocs]
ignore_cache = true
docstring_style = "Numpydocs"
codegen_server = "http://localhost:8000/v1"
```
The internal pydantic struct [`PyGenDocsConfiguration`](./src/pygendocs/config.py#L23) outlines all supported configuration options. Refer to that struct for supported options and their syntax.

## LLM integration and self-hosting 🤖
> 👷‍♂️ tbd
