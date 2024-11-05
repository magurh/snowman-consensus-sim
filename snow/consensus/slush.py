from snow.node.network import Network
from snow.node.node import (
    FixedNode,
    Node,
    OffNode,
)


class SlushNode(Node):
    def __init__(
        self,
        node_id: int,
        initial_state: int,
        sample_size: int,
        quorum: int,
    ) -> None:
        super().__init__(node_id, initial_state, sample_size)
        self.quorum = quorum

    def update_state(
        self,
        sampled_states: list[Node],
    ) -> None:
        """Updates the node's preferred state if the sampled majority meets quorum."""
        if self.finalized:
            return

        # Count occurrences of each state in the sampled nodes
        state_counts = {
            state: sampled_states.count(state) for state in set(sampled_states)
        }

        # Determine the majority state if it meets quorum
        majority_state, count = max(state_counts.items(), key=lambda item: item[1])

        if count >= self.quorum:
            self.preferred_state = majority_state


class SlushNetwork(Network):
    def __init__(
        self,
        nodes: list[Node],
    ) -> None:
        super().__init__(nodes)  # Initialize the base Network class

    @classmethod
    def initialize_network(
        cls,
        num_nodes: int,
        initial_states: list[int],
        sample_size: int,
        quorum: int,
        fixed_nodes: int = 0,
        off_nodes: int = 0,
    ) -> None:
        """
        Creates and initializes a Slush network of nodes with given configuration.
        """
        nodes = []

        # Initialize honest nodes
        honest_nodes = num_nodes - fixed_nodes - off_nodes
        nodes += [
            SlushNode(
                node_id=i,
                initial_state=initial_states[i],
                sample_size=sample_size,
                quorum=quorum,
            )
            for i in range(honest_nodes)
        ]

        # Initialize fixed nodes
        nodes += [
            FixedNode(
                node_id=i,
                initial_state=initial_states[i],
            )
            for i in range(honest_nodes, honest_nodes + fixed_nodes)
        ]

        # Initialized offline nodes
        nodes += [
            OffNode(
                node_id=i,
                initial_state=initial_states[i],
                sample_size=sample_size,
            )
            for i in range(honest_nodes + fixed_nodes, num_nodes)
        ]

        return cls(nodes)
