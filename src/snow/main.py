from src.snow.config import SimConfig, SnowballConfig
from src.snow.network import LockstepNetwork
from src.snow.node import TYPES
from src.snow.sampler import UniformSampler
from src.snow.simulation import run_simulation
from src.snow.utils import saver


def start() -> None:
    """Run simulation."""
    snowball = SnowballConfig(
        K=21,
        AlphaPreference=11,
        AlphaConfidence=11,
        Beta=30,
    )

    sim_config = SimConfig(
        num_nodes=250,
        num_iterations=10,
        snowball=snowball,
        node_counts={TYPES.honest: 250},
        initial_preferences={TYPES.honest: [0] * 125 + [1] * 125},  # type: ignore[arg-type]
    )

    results = run_simulation(
        network_class=LockstepNetwork,
        sampler=UniformSampler(),
        sim_config=sim_config,
        finality="partial",
    )

    saver.save_json(results, "lockstep_partial_finality.json")


if __name__ == "__main__":
    start()
