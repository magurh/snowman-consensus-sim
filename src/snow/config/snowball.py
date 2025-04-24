from dataclasses import dataclass


@dataclass
class SnowballConfig:
    """Snowball Config class."""

    K: int
    AlphaPreference: int
    AlphaConfidence: int
    Beta: int
