from typing import override

from src.config import SnowballConfig

from .base import BaseNode
from .type import TYPES


class OfflineNode(BaseNode):
    """Node that never replies to queries."""

    def __init__(self, node_id: int, snowball_params: SnowballConfig) -> None:
        """Initialize an offline node."""
        super().__init__(
            node_id, initial_preference=None, snowball_params=snowball_params
        )
        self.finalized = True
        self.type: str = TYPES.offline

    @override
    def on_query(self, peer_preference: int | None) -> int | None:
        """Always return None."""
        return None


class FixedNode(BaseNode):
    """Node that always returns a fixed preference."""

    def __init__(
        self, node_id: int, fixed_preference: int, snowball_params: SnowballConfig
    ) -> None:
        """Initialize a fixed-decision node."""
        super().__init__(
            node_id,
            initial_preference=fixed_preference,
            snowball_params=snowball_params,
        )
        self.finalized = True
        self.type: str = TYPES.fixed

    @override
    def on_query(self, peer_preference: int | None) -> int | None:
        """Always returns the fixed preference."""
        return self.preference


class LNode(BaseNode):
    """Liveness attack node."""

    def __init__(self, node_id: int, snowball_params: SnowballConfig) -> None:
        """Initialize an L-node."""
        super().__init__(
            node_id, initial_preference=None, snowball_params=snowball_params
        )
        self.network_distribution: dict[int, int] = {}
        self.type: str = TYPES.dynamic

    def update_distribution(self, distribution: dict[int, int]) -> None:
        """
        Update the internal view of the network's preference distribution.

        Args:
            distribution: A mapping from preference value (0 or 1) to count.

        """
        self.network_distribution = distribution

    @override
    def on_query(self, peer_preference: int | None) -> int:
        """Respond with the minority preference."""
        count_0 = self.network_distribution.get(0, 0)
        count_1 = self.network_distribution.get(1, 0)

        return 0 if count_1 > count_0 else 1
