from config.config import config
from snow.consensus.snowflake import SnowflakeNetwork


class SnowflakeSimulation:
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
        self.network = SnowflakeNetwork.initialize_network(
            num_nodes=num_nodes,
            initial_states=initial_states,
            sample_size=sample_size,
            quorum=quorum,
            beta=beta,
            fixed_nodes=fixed_nodes,
            off_nodes=off_nodes,
        )

    def run(self, rounds: int = config.snowflake_rounds) -> None:
        """Run the Snowflake consensus simulation for the specified number of rounds."""
        print(f"Initial distribution: {self.network.get_distribution()}")
        for round_num in range(rounds):
            for node in self.network.nodes:
                if node.finalized:
                    continue  # Skip nodes that have already finalized their state

                sampled_nodes = node.sample_network(self.network.nodes)
                sampled_states = [n.preferred_state for n in sampled_nodes]
                node.update_state(
                    sampled_states
                )  # Each node updates its state based on the sampled states

            distribution = self.network.get_distribution()
            print(f"Round {round_num + 1} distribution: {distribution}")

            # Check if all nodes have finalized to potentially end the simulation early
            if all(node.finalized for node in self.network.nodes):
                print("All nodes have finalized their states. Ending simulation.")
                break
