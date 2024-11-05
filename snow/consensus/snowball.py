from snow.node.network import Network
from snow.node.node import (
    FixedNode,
    Node,
    OffNode,
)


class SnowballNode(Node):
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
        self.counter = 0  # Consecutive rounds with no change
        self.state_confidence = [0, 0]  # Binary confidence counters

    def update_state(
        self,
        sampled_states: list[int],
    ) -> None:
        """Updates preferred state based on majority and confidence."""
        if self.finalized:
            return

        # Count occurrences of each state in the sampled nodes
        state_counts = {
            state: sampled_states.count(state) for state in set(sampled_states)
        }

        # Determine the majority state if it meets quorum
        majority_state, count = max(state_counts.items(), key=lambda item: item[1])

        # Check if majority meets quorum and matches current state
        if count >= self.quorum:
            if majority_state == self.preferred_state:
                # Increase both consecutive and state-specific confidence
                self.counter += 1
                self.state_confidence[majority_state] += 1

                # Finalize if confidence threshold beta is met
                if self.counter >= self.beta:
                    self.finalized = True
            else:
                # Update preferred state and reset consecutive confidence
                # Only switch if opposite state confidence is higher
                if (
                    self.state_confidence[1 - self.preferred_state]
                    > self.state_confidence[self.preferred_state]
                ):
                    self.preferred_state = 1 - self.preferred_state
                    self.counter = 1  # Start new consecutive count
                    # Increase confidence for the newly adopted state
                    self.state_confidence[self.preferred_state] += 1


class SnowballNetwork(Network):
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
        Creates and initializes a Snowball network of nodes with given configuration.
        """
        nodes = []

        # Initialize honest Snowflake nodes
        honest_nodes = num_nodes - fixed_nodes - off_nodes
        nodes += [
            SnowballNode(
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
