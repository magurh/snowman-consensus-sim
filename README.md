[![python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org) [![jupyter](https://img.shields.io/badge/Jupyter-Lab-F37626.svg?style=flat&logo=Jupyter)](https://jupyterlab.readthedocs.io/en/stable) 

# Consensus Protocols

## Setup

Poetry is used for dependency management. Whenever new dependencies are added, run:
```
poetry install
```
To use Jupyter Lab, set the kernel to the fast-updates-monitoring environment created by poetry:
```
poetry run python -m ipykernel install --user --name=flare-boosting
poetry run jupyter lab
```
For simply activating the virtual environment, run `poetry shell`. To add new dependencies, use `poetry add <dependency>`.
