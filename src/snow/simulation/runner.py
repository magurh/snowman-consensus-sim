from tqdm import trange

from src.config import SimConfig
from src.snow.network import BaseNetwork
from src.snow.sampler import Sampler


def run_simulation(
    network_class: type[BaseNetwork],
    sampler: Sampler,
    sim_config: SimConfig,
    finality: str = "full",  # or "partial"
) -> list[dict]:
    """
    Run multiple network simulations with identical parameters.

    Returns:
        List of finalization stats dicts (one per run).

    """
    results = []

    for _ in trange(sim_config.num_iterations, desc="Running simulations"):
        net = network_class(
            node_counts=sim_config.node_counts,
            initial_preferences=sim_config.initial_preferences,
            snowball_params=sim_config.snowball,
            sampler=sampler,
        )

        while True:
            net.run_round()
            if finality == "partial" and net.check_partial_finalization():
                break
            if finality == "full" and net.check_honest_finalization():
                break

        results.append(net.get_finalization_stats())

    return results
