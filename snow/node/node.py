import random


class Node:
    def __init__(self, node_id: int, initial_state: int, sample_size: int) -> None:
        self.node_id = node_id
        self.preferred_state = initial_state  # Initial preferred state (0 or 1)
        self.confidence = 0  # Confidence counter
        self.finalized = False  # Finalized status
        self.sample_size = sample_size

    def sample_network(self, network: list) -> list:
        """Samples a subset of nodes from the network."""
        return random.sample(
            [node for node in network if node != self], self.sample_size
        )


class FixedNode(Node):
    """A dishonest node with a fixed preference that never changes."""

    def __init__(self, node_id: int, initial_state: int, sample_size: int) -> None:
        super().__init__(node_id, initial_state, sample_size)

    def update_state(self, _) -> None:
        """Ignores the sampled states and keeps its initial preference."""
        # Does nothing, keeping the initial preferred state
        pass


class OffNode(Node):
    """A dishonest node that chooses the opposite of the majority sample."""

    def __init__(self, node_id: int, initial_state: int, sample_size: int) -> None:
        super().__init__(node_id, initial_state, sample_size)

    def update_state(self, sampled_states: list) -> None:
        """Switches preference to the opposite of the majority in the sample."""
        if self.finalized:
            return

        # Count occurrences of each state
        state_counts = {
            state: sampled_states.count(state) for state in set(sampled_states)
        }
        majority_state, count = max(state_counts.items(), key=lambda item: item[1])

        # Determine the anti-majority preference (opposite of majority)
        new_preference = 1 if majority_state == 0 else 0
        self.preferred_state = new_preference
