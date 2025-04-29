from typing import override

import numpy as np

from src.config import SnowballConfig
from src.snow.node import LNode
from src.snow.sampler import Sampler

from .base import BaseNetwork


class RandomSamplingNetwork(BaseNetwork):
    """Execute one Snowball round for a single honest node."""

    def __init__(
        self,
        node_counts: dict[str, int],
        initial_preferences: dict[str, list[int | None]],
        snowball_params: SnowballConfig,
        sampler: Sampler,
    ) -> None:
        super().__init__(node_counts, initial_preferences, snowball_params, sampler)

    @override
    def run_round(self) -> None:
        """Execute a single round of the protocol."""
        self._update_adversary_distributions()

        unfinished = self.honest_nodes[[not n.finalized for n in self.honest_nodes]]
        if unfinished.size == 0:
            return

        rng = np.random.default_rng()
        node = rng.choice(unfinished)

        peers = self.sampler.sample(node, self.nodes, self.snowball_params.K)
        preferences = np.array([peer.on_query(node.preference) for peer in peers])
        node.snowball_round(preferences)

        self._update_finalization_stats()
        self.round += 1

    def _update_adversary_distributions(self) -> None:
        dist = self._get_distribution()
        for node in self.nodes:
            if isinstance(node, LNode):
                node.update_distribution(dist)
