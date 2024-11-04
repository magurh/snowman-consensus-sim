[![python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org) [![jupyter](https://img.shields.io/badge/Jupyter-Lab-F37626.svg?style=flat&logo=Jupyter)](https://jupyterlab.readthedocs.io/en/stable) 

# Consensus Protocols

## Setup

uv is used for dependency management. To install all dependencies, run:
```
uv sync --all-extras
```
To use Jupyter Lab, set-up a kernel:
```
uv run python -m ipykernel install --user --name=snowman
uv run jupyter lab
```
For simply activating the virtual environment, run `uv shell`. To add new dependencies, use `uv add <dependency>`.
