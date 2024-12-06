from config.config import config
from snow.consensus.snowball import SnowballNetwork


class SnowballSimulation:
    def __init__(
        self,
        num_nodes: int = config.num_nodes,
        fixed_nodes: int = config.fixed_nodes,
        off_nodes: int = config.off_nodes,
        initial_states: list[int] = config.initial_states,
        sample_size: int = config.K,
        quorum: int = config.Alpha,
        beta: int = config.Beta,
    ) -> None:
        self.network = SnowballNetwork.initialize_network(
            num_nodes=num_nodes,
            initial_states=initial_states,
            sample_size=sample_size,
            quorum=quorum,
            beta=beta,
            fixed_nodes=fixed_nodes,
            off_nodes=off_nodes,
        )

    def run(self) -> tuple[dict, int]:
        """Run the Snowball consensus simulation."""
        print(f"Initial distribution: {self.network.get_distribution()}")

        while True:
            for node in self.network.nodes:
                if node.finalized:
                    continue  # Skip nodes that have already finalized their state

                sampled_nodes = node.sample_network(self.network.nodes)
                sampled_states = [n.preferred_state for n in sampled_nodes]
                node.update_state(sampled_states)  # Update based on sampled states

            state_distribution = self.network.get_distribution()
            # print(f"Round {round_num + 1} distribution: {state_distribution}")

            # End simulation early if all nodes are finalized
            if all(node.finalized for node in self.network.nodes):
                print("All nodes have finalized their states. Ending simulation.")
                break

        # Extract the number of rounds taken by each node for the distribution report
        rounds_distribution = self.network.get_round_distribution()

        return state_distribution, rounds_distribution
