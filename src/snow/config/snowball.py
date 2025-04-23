from dataclasses import dataclass


@dataclass
class SnowballConfig:
    K: int
    AlphaPreference: int
    AlphaConfidence: int
    Beta: int
