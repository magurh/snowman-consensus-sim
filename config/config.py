from dataclasses import dataclass


@dataclass
class Config:
    num_nodes: int
    initial_states: list[int]
    algorithm: str  # 'slush', 'snowflake', or 'snowball'
    K: int  # Number of nodes to sample in each round
    Alpha: int
    BetaVirtuous: int  # Used for Snowflake and Snowball
    BetaRogue: int  # Used for Snowflake and Snowball
    slush_rounds: int
    fixed_nodes: int  # nodes with fixed preference state
    off_nodes: int  # nodes that update state against majority


config = Config(
    num_nodes=100,
    initial_states=[0 for j in range(100)],
    algorithm="slush",
    K=20,
    Alpha=15,
    BetaVirtuous=15,
    BetaRogue=20,
    slush_rounds=20,
    fixed_nodes=0,
    off_nodes=0,
)
