from dataclasses import dataclass


@dataclass
class Config:
    num_nodes: int
    K: int  # Number of nodes to sample in each round
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
