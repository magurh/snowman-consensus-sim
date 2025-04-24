from typing import override

import numpy as np

from src.snow.node import BaseNode

from .base import Sampler


class UniformSampler(Sampler):
    """Uniformly random sampling."""

    @override
    def sample(self, node: BaseNode, all_nodes: np.ndarray, k: int) -> np.ndarray:
        """
        Method for sampling k nodes excluding 'node'.

        Args:
            node: node doing the sampling.
            all_nodes: full list of nodes.
            k: sample size.

        Returns:
            A list of sampled nodes.

        """
        all_nodes = np.asarray(all_nodes, dtype=object)
        mask = np.array([n.node_id != node.node_id for n in all_nodes])
        candidates = all_nodes[mask]

        rng = np.random.default_rng()
        return rng.choice(candidates, size=k, replace=False)
