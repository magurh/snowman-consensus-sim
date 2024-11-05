from snow.node.network import Network
from snow.node.node import (
    FixedNode,
    Node,
    OffNode,
)


class SnowflakeNode(Node):
    def __init__(
        self,
        node_id: int,
        initial_state: int,
        sample_size: int,
        quorum: int,
        beta: int,
    ) -> None:
        super().__init__(node_id, initial_state, sample_size)
        self.quorum = quorum
        self.beta = beta
        self.counter = 0  # Initialize the counter

    def update_state(
        self,
        sampled_states: list[int],
    ) -> None:
        """Update preferred state based on quorum and counter."""
        if self.finalized:
            return

        # Update number of rounds parameter
        self.count_round()

        # Count occurrences of each state in the sampled nodes
        state_counts = {
            state: sampled_states.count(state) for state in set(sampled_states)
        }

        # Determine the majority state and its count
        majority_state, count = max(state_counts.items(), key=lambda item: item[1])

        # Update the node's state and consecutive_queries
        if count >= self.quorum:
            if majority_state == self.preferred_state:
                # If the majority matches the preferred state, increase counter
                self.counter += 1
                if self.counter >= self.beta:
                    # Finalize the state if counter reaches beta
                    self.finalized = True
            else:
                # Change preferred state and reset counter to 1
                self.preferred_state = majority_state
                self.counter = 1


class SnowflakeNetwork(Network):
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
        beta: int,
        fixed_nodes: int = 0,
        off_nodes: int = 0,
    ) -> None:
        """
        Creates and initializes a Snowflake network of nodes with given configuration.
        """
        nodes = []

        # Initialize honest Snowflake nodes
        honest_nodes = num_nodes - fixed_nodes - off_nodes
        nodes += [
            SnowflakeNode(
                node_id=i,
                initial_state=initial_states[i],
                sample_size=sample_size,
                quorum=quorum,
                beta=beta,
            )
            for i in range(honest_nodes)
        ]

        # Initialize fixed nodes
        nodes += [
            FixedNode(
                node_id=i,
                initial_state=initial_states[i],
                sample_size=sample_size,
            )
            for i in range(honest_nodes, honest_nodes + fixed_nodes)
        ]

        # Initialize offline nodes
        nodes += [
            OffNode(
                node_id=i,
                initial_state=initial_states[i],
                sample_size=sample_size,
            )
            for i in range(honest_nodes + fixed_nodes, num_nodes)
        ]

        return cls(nodes)
