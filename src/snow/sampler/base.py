from abc import ABC, abstractmethod

from src.snow.node import BaseNode


class Sampler(ABC):
    """Base sampling class."""

    @abstractmethod
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
