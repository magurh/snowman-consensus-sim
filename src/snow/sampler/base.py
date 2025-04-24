from abc import ABC, abstractmethod

import numpy as np

from src.snow.node import BaseNode


class Sampler(ABC):
    """Base sampling class."""

    @abstractmethod
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
