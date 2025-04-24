from dataclasses import dataclass


@dataclass
class SnowballConfig:
    """Snowball Config class."""

    K: int
    AlphaPreference: int
    AlphaConfidence: int
    Beta: int


@dataclass
class SimConfig:
    """General configuration."""

    num_nodes: int
    num_iterations: int
    snowball: SnowballConfig
    node_counts: dict[str, int]
    initial_preferences: dict[str, list[int | None]]
