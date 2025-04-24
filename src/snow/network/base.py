from abc import ABC, abstractmethod

from src.snow.config import SnowballConfig
from src.snow.node import BaseNode, make_node
from src.snow.sampler import Sampler


class BaseNetwork(ABC):
    """Abstract base class for a Snowball node network."""

    def __init__(
        self,
        node_counts: dict[str, int],
        initial_preferences: dict[str, list[int | None]],
        snowball_params: SnowballConfig,
        sampler: Sampler,
    ) -> None:
        """
        Initialize network with a mix of node types and preferences.

        Args:
            node_counts: Dict mapping node type to count.
            initial_preferences: Dict mapping node type to list of preferences.
            snowball_params: Snowball protocol parameters.
            sampler: chosen sampler.

        """
        self.round: int = 0
        self.snowball_params: SnowballConfig = snowball_params
        self.sampler = sampler
        self.nodes: list[BaseNode] = []
        self.finalized_rounds: dict[int, int] = {}

        node_id = 0
        for node_type, count in node_counts.items():
            prefs = initial_preferences.get(node_type, [None] * count)
            if len(prefs) != count:
                msg = f"Preference list for '{node_type}' must match count {count}."
                raise ValueError(msg)

            for pref in prefs:
                try:
                    node = make_node(node_type, node_id, pref, snowball_params)
                except ValueError as err:
                    msg = f"Error creating node {node_id} of type '{node_type}': {err}"
                    raise ValueError(msg) from err

                self.nodes.append(node)
                node_id += 1

        self.honest_nodes: list[BaseNode] = [n for n in self.nodes if n.is_honest()]

    def _get_distribution(self) -> dict[int, int]:
        """Return the current network preference distribution."""
        dist: dict[int, int] = {0: 0, 1: 0}
        for node in self.nodes:
            if node.preference in (0, 1):
                dist[node.preference] += 1
        return dist

    def _update_finalization_stats(self) -> None:
        """Update finalized round records for honest nodes."""
        for node in self.honest_nodes:
            if node.finalized and node.node_id not in self.finalized_rounds:
                self.finalized_rounds[node.node_id] = self.round

    def check_partial_finalization(self) -> bool:
        """
        Check if >50% of honest nodes are finalized.

        Returns:
            True if partial finalization is reached.

        """
        finalized = [n for n in self.honest_nodes if n.finalized]
        return len(finalized) > len(self.honest_nodes) // 2

    def check_honest_finalization(self) -> bool:
        """
        Check if all honest nodes are finalized.

        Returns:
            True if full finalization is reached.

        """
        return all(n.finalized for n in self.honest_nodes)

    def get_finalization_stats(self) -> dict:
        """
        Report finalization stats after simulation.

        Returns:
            Dict with finalization rounds,
            per-node finalized rounds,
            and preference distribution.

        """
        return {
            "rounds_to_partial": self.round
            if self.check_partial_finalization()
            else None,
            "rounds_to_full": self.round if self.check_honest_finalization() else None,
            "per_node_rounds": self.finalized_rounds,
            "distribution": self._get_distribution(),
        }

    @abstractmethod
    def run_round(self) -> None:
        """Execute a single round of the protocol."""
