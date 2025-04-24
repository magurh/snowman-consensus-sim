from typing import override

import numpy as np

from src.snow.node import BaseNode

from .base import Sampler


class UniformSampler(Sampler):
    """Uniformly random sampling."""

    @override
    def sample(
        self, node: BaseNode, all_nodes: list[BaseNode], k: int
    ) -> list[BaseNode]:
        """
        Method for sampling k nodes excluding 'node'.

        Args:
            node: node doing the sampling.
            all_nodes: full list of nodes.
            k: sample size.

        Returns:
            A list of sampled nodes.

        """
        candidates = [n for n in all_nodes if n.node_id != node.node_id]
        rng = np.random.default_rng()
        return rng.choice(candidates, size=k, replace=False).tolist()  # type: ignore[arg-type]
