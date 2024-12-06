[![python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![jupyter](https://img.shields.io/badge/Jupyter-Lab-F37626.svg?style=flat&logo=Jupyter)](https://jupyterlab.readthedocs.io/en/stable) 
![Go](https://img.shields.io/badge/Golang-1.21.8-%2300ADD8.svg?style=flate&logo=go&logoColor=white)


# Consensus Protocols

This repository offers Python implementations of the Snow consensus protocols, currently implemented on Avalanche-like blockchains.
A clone of the latest `go-flare` node written in Go is included for testing how parameters affect performance.

## go-flare Testing

For testing functionality of `go-flare`, navigate to the desired subdirectory and run:
```bash
go test -v -run <TestFunction>
```
Here the `-v` flag is optional and is used to ensure that logged outputs are displayed.


## Setup

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
