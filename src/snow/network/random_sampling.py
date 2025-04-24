from typing import override

import numpy as np

from src.node import LNode
from src.snow.config import SnowballConfig
from src.snow.sampler import Sampler

from .base import BaseNetwork


class RandomSamplingNetwork(BaseNetwork):
    """
    Execute one Snowball round for a single, random, non-finalized honest node.
    """

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

        unfinished = [n for n in self.honest_nodes if not n.finalized]
        if not unfinished:
            return

        node = np.random.default_rng().choice(unfinished)
        peers = self.sampler.sample(node, self.nodes, self.snowball_params.K)
        preferences = [peer.on_query(node.preference) for peer in peers]
        node.snowball_round(preferences)

        self._update_finalization_stats()
        self.round += 1

    def _update_adversary_distributions(self) -> None:
        dist = self._get_distribution()
        for node in self.nodes:
            if isinstance(node, LNode):
                node.update_distribution(dist)
