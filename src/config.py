from dataclasses import dataclass
from typing import Any


@dataclass
class SnowballConfig:
    """Snowball Config class."""

    K: int
    AlphaPreference: int
    AlphaConfidence: int
    Beta: int

    def update(self, **kwargs: Any) -> None:
        """Update SnowballConfig parameters in-place."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                e = f"Invalid SnowballConfig field: {key}"
                raise ValueError(e)


@dataclass
class SimConfig:
    """General configuration."""

    num_nodes: int
    num_iterations: int
    snowball: SnowballConfig
    node_counts: dict[str, int]
    initial_preferences: dict[str, list[int | None]]

    def update_snowball(self, **kwargs: Any) -> None:
        """Update nested SnowballConfig."""
        self.snowball.update(**kwargs)
