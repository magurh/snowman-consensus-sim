from dataclasses import dataclass, field

import numpy as np


@dataclass
class SnowballSampler:
    """Holds the fixed state needed to sample peers."""

    rng: np.random.Generator
    sample_size: int = field(default=0, init=False)
    num_nodes: int = field(default=0, init=False)
    lnode_start: int = field(default=0, init=False)

    def update_config(self, sample_size: int, num_nodes: int, lnode_start: int) -> None:
        """Update Class config."""
        self.sample_size = sample_size
        self.num_nodes = num_nodes
        self.lnode_start = lnode_start

    def check_config(self) -> None:
        """Ensure configuration is complete before sampling."""
        if 0 in (self.sample_size, self.num_nodes, self.lnode_start):
            e = "SnowballSampler is not fully configured."
            raise RuntimeError(e)

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
        u = self.rng.choice(self.num_nodes - 1, size=self.sample_size, replace=False)
        sampled = u + (u >= node_id)

        # 2) Get prefs, overriding L-nodes
        sampled_prefs = preferences[sampled]
        if self.lnode_start < self.num_nodes:
            lmask = sampled >= self.lnode_start
            if lmask.any():
                sampled_prefs[lmask] = lnode_pref

        # 3) Count 1s vs 0s
        ones = int(sampled_prefs.sum())
        zeros = self.sample_size - ones

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
        """Sample peers for all active nodes and parse votes."""
        peer_samples = np.empty((active_nodes.size, self.sample_size), dtype=int)

        for idx, node_id in enumerate(active_nodes):
            # draw K distinct peers from [0..N-2]
            u = self.rng.choice(
                self.num_nodes - 1, size=self.sample_size, replace=False
            )
            # shift those ≥ node_id up by 1 to skip self
            peer_samples[idx] = u + (u >= node_id)

        # Gather preferences and override LNode values
        sampled_prefs = preferences[peer_samples].copy()  # shape (M, K)
        if self.lnode_start < self.num_nodes:
            lnode_mask = peer_samples >= self.lnode_start
            if lnode_mask.any():
                sampled_prefs[lnode_mask] = lnode_pref

        # Count zeros/ones
        ones = sampled_prefs.sum(axis=1).astype(int)
        zeros = self.sample_size - ones

        # Return preferences and counts
        majority_pref = (ones > zeros).astype(np.uint8)
        majority_count = np.where(ones > zeros, ones, zeros)

        return majority_pref, majority_count
