from dataclasses import dataclass

import numpy as np


@dataclass
class SnowballSampler:
    """Holds the fixed state needed to sample peers."""

    K: int
    num_nodes: int
    lnode_start: int
    rng: np.random.Generator

    def choose_node(
        self,
        active_nodes: np.ndarray,
    ) -> int:
        """Randomly select a node from active nodes."""

        node_id = self.rng.choice(active_nodes)

        return node_id

    def sample_and_count(
        self,
        node_id: int,
        preferences: np.ndarray,
        lnode_pref: int,
    ) -> tuple[int, int]:
        """
        Sample K peers and count how many votes for 0 vs. 1.

        Args:
            node_id: The index of the honest node doing the sampling.
            preferences: 1d array of preferences.
            lnode_pref: preference of LNodes.

        Returns:
            (preference, count) giving the majority and count of votes.

        """
        # 1) Draw from [0..num_nodes-2], then shift ≥node_id up by 1
        u = self.rng.integers(0, self.num_nodes - 1, size=self.K)
        sampled = u + (u >= node_id)

        # 2) Get prefs, overriding L-nodes
        sampled_prefs = preferences[sampled]
        lmask = sampled >= self.lnode_start
        if lmask.any():
            sampled_prefs[lmask] = lnode_pref

        # 3) Count 1s vs 0s
        ones = int(sampled_prefs.sum())
        zeros = self.K - ones

        # 4) Get preference and count
        if ones > zeros:
            majority_pref = 1
            majority_count = ones
        else:
            majority_pref = 0
            majority_count = zeros

        return majority_pref, majority_count
