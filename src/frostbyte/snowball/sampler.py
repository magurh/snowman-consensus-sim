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
        return self.rng.choice(active_nodes)

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

    def batch_sampler(
        self,
        active_nodes: np.ndarray,
        preferences: np.ndarray,
        lnode_pref: int,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Sample K peers for all active nodes and parse votes."""
        peer_samples = np.empty((active_nodes.size, self.K), dtype=int)

        for idx, node_id in enumerate(active_nodes):
            # draw K distinct peers from [0..N-2]
            u = self.rng.choice(self.num_nodes - 1, size=self.K, replace=False)
            # shift those ≥ node_id up by 1 to skip self
            peer_samples[idx] = u + (u >= node_id)

        # Gather preferences and override LNode values
        sampled_prefs = preferences[peer_samples]  # shape (M, K)
        lnode_mask = peer_samples >= self.lnode_start
        sampled_prefs[lnode_mask] = lnode_pref

        # Count zeros/ones
        ones = sampled_prefs.sum(axis=1).astype(int)
        zeros = self.K - ones

        # Return preferences and counts
        majority_pref = (ones > zeros).astype(np.uint8)
        majority_count = np.where(ones > zeros, ones, zeros)

        return majority_pref, majority_count
