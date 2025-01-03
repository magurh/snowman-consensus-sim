[![python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![jupyter](https://img.shields.io/badge/Jupyter-Lab-F37626.svg?style=flat&logo=Jupyter)](https://jupyterlab.readthedocs.io/en/stable) 
![Go](https://img.shields.io/badge/Golang-1.21.8-%2300ADD8.svg?style=flate&logo=go&logoColor=white)


# Consensus Protocols

This repository offers Python implementations of the Snow consensus protocols, currently implemented on Avalanche-like blockchains.
A clone of the latest `go-flare` node written in Go is included for testing how parameters affect performance.

## Repository Setup

### Cloning Submodules

When cloning the repository, one needs to initialize and pull the `go-flare` submodule:
```bash
git clone --recurse-submodules https://github.com/magurh/snowman-consensus.git
```
Otherwise, the submodule needs to be initialized manually using `git submodule init` from the submodule folder.
The submodule should point to a fork of `go-flare` available [here](https://github.com/magurh/go-flare).

When commiting changes make sure to commit changes inside the submodule, as well as changes in the main repo.
### Dependencies
uv is used for dependency management. To install all dependencies, run:
```bash
uv sync --all-extras
```
To use Jupyter Lab, set-up a kernel:
```bash
uv run python -m ipykernel install --user --name=snowman
uv run jupyter lab
```
For simply activating the virtual environment, run `uv shell`. To add new dependencies, use `uv add <dependency>`.
For formatting and linting use:
```bash
uv run ruff format
uv run ruff check
```

## go-flare Testing
For testing functionality of `go-flare`, navigate to the desired subdirectory and run:
```bash
go test -v -run <TestFunction>
```
Here the `-v` flag is optional and is used to ensure that logged outputs are displayed.
Ensure that general Go guidelines are satisfied:
* Test scripts are of the form `<script>_test.go`.
* Test functions are of the form `Test<Function>()` and accept a single argument of type `*testing.T`.
* Use `t.Log` or `t.Logf` for debugging.