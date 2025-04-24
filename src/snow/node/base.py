from abc import ABC, abstractmethod

from src.snow.config import SnowballConfig


class BaseNode(ABC):
    """Base class for all node types in the Snowball protocol."""

    def __init__(
        self,
        node_id: int,
        initial_preference: int | None,
        snowball_params: SnowballConfig,
    ) -> None:
        """
        Initialize a base node.

        Args:
            node_id: Unique identifier for the node.
            initial_preference: The node's initial preference (0, 1, or None).
            snowball_params: snowball configuration.

        """
        self.node_id: int = node_id
        self.preference: int | None = initial_preference
        self.finalized: bool = False
        self.snowball_params: SnowballConfig = snowball_params
        self.type: str = ""

    @abstractmethod
    def on_query(self, peer_preference: int | None) -> int | None:
        """Respond to a query from a peer."""

    def update_snow_params(self, snowball_params: SnowballConfig) -> None:
        """Update Snowball parameters."""
        self.snowball_params = snowball_params

    def return_type(self) -> str:
        """Return node type."""
        return self.type
