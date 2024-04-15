<p align="center"></p>
<h2 align="center">Staging</h2>
<p align="center">
<a href="https://github.com/rgryta/Staging/actions/workflows/main.yml"><img alt="Build" src="https://github.com/rgryta/Staging/actions/workflows/main.yml/badge.svg?branch=main"></a>
<a href="https://pypi.org/project/staging/"><img alt="PyPI" src="https://img.shields.io/pypi/v/staging"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://github.com/PyCQA/pylint"><img alt="pylint" src="https://img.shields.io/badge/linting-pylint-yellowgreen"></a>
<a href="https://github.com/rgryta/NoPrint"><img alt="NoPrint" src="https://img.shields.io/badge/NoPrint-enabled-blueviolet"></a>
</p>

## About

Automate your commands - be it for environment setup or in CI/CD pipeline. Parallelize execution, and make it easier to handle dependent commands.

## Requirements

This package requires `tomlkit` and `dataclass-wizard` packages.

## Usage

### Full description
Staging is configurable in `pyproject.toml` file and is accessible through CLI interface.

In order to use staging, you have to define steps and then stages. Stages are built from steps.

Let's see example below (which uses all available options):

```toml
[tool.staging.steps]
# Test
get_test_packages = {execute = "command to get test packages", output="test_packages"}
coverage = { prepare = "coverage run -m pytest -xv {packages}", execute = "coverage report {flags}", cleanup = "coverage erase", output = "coverage_result", format = {flags = "flags", packages= "test_packages"} }
# Lint
clean = {execute = "command to execute", success_codes=[0,1,2,3,4,5]}
isort = { execute = "isort {flags} . tests", format = {flags = "flags"}}
black = { execute = "black {flags} . tests", format = {flags = "flags"}}
pylint = { execute = "pylint {package} tests", format = {package = "package"}}
noprint = { execute = "noprint -ve {package} tests", format = {package = "package"}, error_codes=[1,2]}
finish = { execute = "finishing command" }

[tool.staging.stages.format]
description = "Format code"
format = {package="staging"}
steps = [
    {step = "isort"},
    {step = "black"},
]

[tool.staging.stages.lint]
description = "Check linting"
format = {flags="--check", package="staging"}
steps = [
    {step = "clean", continue_on_failure=true},
    {parallel = {steps = ["isort", "black", "pylint", "noprint"]}, continue_on_failure=true},
    {step = "finish"},
]

[tool.staging.stages.test]
description = "Test the package"
format = {flags="-m --fail-under=30"}
steps = [
    {step = "get_test_packages"},
    {step = "coverage"},
]
```

Here we have defined 7 different steps: `get_test_packages`, `coverage`, `clean`, and so on.
These 7 steps are later used in 3 stages: `test`, `lint`, and `format`.

Let's say we execute `staging format`. What happens?
1. Stage context is updated with formatter {key=`package`, value=`staging`}.
2. Step `isort` is executed. Command `isort {flags} . tests` is formatted using stage formatter. Since flags is empty, 
the final command is simply `isort  . tests`.
3. Step `black` is executed. This works the same as `isort` above.

Now let's say we execute `staging lint`.
1. Context has formatter for value `package`, but also for `flags`.
2. Step `clean` is executed. It might fail, but we don't care and instead the process is continued.
3. Steps `isort`, `black`, `pylint` and `noprint` are all executed in a thread pool due to being specified in a `parallel` block. 
This time however, even though some of the steps are the same as in the `staging format`, we now have a `flags` formatter defined.
Thanks to this, we now have executed `isort --check . tests` command that would verify if the formatting was properly applied. 
Due to how steps are configured - specified custom success and error codes - the parallel block would fail (one command will crash others). 
However, the parallel block allows to specify `continue_on_error` as well, just like step block.
4. As such, `finish` block is also executed.

Last but not least, `staging test`.
1. Similarly to previous stages, we set up the stage formatter context.
2. Step `get_test_packages` outputs a package name to stdout. This value will be saved under `test_packages` key in the staging context.
3. Step `coverage` has a bit of a different structure, it has `prepare` and `cleanup` blocks on top of typical `execute`. 
Prepare is executed before `execute`. However, it's not taken into account when writing to output. Moreover, it will always
fail when status code is different to 0. Block called `cleanup` is just like what it says it is. It's a cleanup process executed after `execute`.
It will be executed no matter what is the final status of the `execute` command.

You can also chain your stages in one command. Keep in mind however that formatting contexts are defined on **per stage** basis.
So if you execute `staging format lint` - formatting context from stage `format` won't be propagated to stage `lint`.
Running stages in one execution is also performed in serial manner - no parallelism.

### Example

For real-life examples, see `pyproject.toml` file for this package.

## Development

### Installation

Install virtual environment and check_bump package in editable mode with dev dependencies.

```bash
python -m venv venv
source venv/bin/activate
pip install -e .[dev]
```


### How to?

Automate as much as we can, see configuration in `pyproject.toml` file to see what are the flags used.

```bash
staging format  # Reformat the code
staging lint    # Check for linting issues
staging test    # Run unit tests and coverage report
```