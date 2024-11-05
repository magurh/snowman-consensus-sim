from .node import Node


class Network:
    def __init__(
        self,
        nodes: list[Node],
    ) -> None:
        self.nodes = nodes  # List of all nodes in the network

    def get_distribution(self) -> dict:
        """Returns the distribution of states across the network."""
        state_counts = {}
        for node in self.nodes:
            state = node.preferred_state
            state_counts[state] = state_counts.get(state, 0) + 1

        return state_counts

    def get_round_distribution(self) -> dict:
        """Returns the distribution of rounds until convergence."""
        round_counts = {}
        for node in self.nodes:
            total_rounds = node.rounds
            round_counts[total_rounds] = round_counts.get(total_rounds, 0) + 1

        return round_counts
