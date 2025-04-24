[![python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![jupyter](https://img.shields.io/badge/Jupyter-Lab-F37626.svg?style=flat&logo=Jupyter)](https://jupyterlab.readthedocs.io/en/stable)
![Go](https://img.shields.io/badge/Golang-1.21.8-%2300ADD8.svg?style=flate&logo=go&logoColor=white)

# Consensus Protocols

This repository offers Python implementations of the Snow consensus protocols, currently implemented on Avalanche-like blockchains.
A clone of the latest `go-flare` node written in Go is included for testing how parameters affect performance.

## Repository Setup

The repository is split into three parts:

* `src/snow`: A `python` implementation of the Snow algorithms which mimics a full network of Snow nodes.
* `src/centralized_gossip`: A very fast `numpy` based implementation of the Snow algorithms, which uses a centralized approach with nodes being simple elements of arrays.
* `go` scripts: contains various `go` scripts for testing the Snow implementation live on blockchains such as Avalanche, or Flare.
    These scripts can be used to get a step-by-step feeling on how Snowman++ works in practice.

### Cloning Submodules

When cloning the repository, one needs to initialize and pull the `go-flare` submodule (if using SSH key for authentication):

```bash
git clone --recurse-submodules git@github.com:magurh/snowman-consensus-sim.git
```

Otherwise, the submodule needs to be initialized manually using `git submodule init` from the submodule folder.
The submodule should point to a fork of `go-flare` available [here](https://github.com/magurh/go-flare), which can be done using:

```bash
git remote set-url origin git@github.com:magurh/go-flare.git
```

When committing changes make sure to commit changes inside the submodule, as well as changes in the main repo.

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
uv run pyright
```

Tests can be run with `pytest`, potentially with additional arguments for showing logs:

```bash
uv run pytest
uv run pytest -o log_cli=true -o log_level=INFO tests/network_test.py
```

### go-flare Testing

For testing functionality of `go-flare`, navigate to the desired subdirectory and run:

```bash
go test -v -run <TestFunction>
```

Here the `-v` flag is optional and is used to ensure that logged outputs are displayed.
Ensure that general Go guidelines are satisfied:

* Test scripts are of the form `<script>_test.go`.
* Test functions are of the form `Test<Function>()` and accept a single argument of type `*testing.T`.
* Use `t.Log` or `t.Logf` for debugging.
