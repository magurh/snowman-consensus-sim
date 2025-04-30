from dataclasses import dataclass

import numpy as np


@dataclass
class SnowballSampler:
    """Holds the fixed state needed to sample peers."""

    K: int
    num_nodes: int
    lnode_start: int
    rng: np.random.Generator

    def sample_and_count(
        self,
        node_id: int,
        preferences: np.ndarray,
        curr_lpref: int,
    ) -> tuple[int, int]:
        """
        Sample K peers and count how many votes for 0 vs. 1.

        Args:
            node_id: The index of the honest node doing the sampling.
            preferences: 1d array of preferences.
            curr_lpref: preference of LNodes.

        Returns:
            (zeros, ones) giving the count of 0-votes and 1-votes.

        """
        # 1) Draw from [0..num_nodes-2], then shift ≥node_id up by 1
        u = self.rng.integers(0, self.num_nodes - 1, size=self.K)
        sampled = u + (u >= node_id)

        # 2) Get prefs, overriding L-nodes
        sampled_prefs = preferences[sampled]
        lmask = sampled >= self.lnode_start
        if lmask.any():
            sampled_prefs[lmask] = curr_lpref

        # 3) Count 1's vs 0's
        ones = int(sampled_prefs.sum())
        zeros = self.K - ones
        return zeros, ones
