from dataclasses import dataclass


@dataclass
class Config:
    """General configuration."""

    num_nodes: int
    K: int
    AlphaPreference: int
    AlphaConfidence: int
    Beta: int


config = Config(
    num_nodes=100,
    K=20,
    AlphaPreference=15,
    AlphaConfidence=15,
    Beta=20,
)
