from collections.abc import Callable
from itertools import accumulate, chain

import numpy as np
from tqdm import trange

from src.config import SimConfig
from src.frostbyte.sampler import SnowballSampler
from src.snow.node import TYPES


def run_snowball(
    sim_config: SimConfig,
    sampler: SnowballSampler,
    snowball_algo: Callable[..., dict],
    finality: str = "full",
) -> list[dict]:
    """
    Run multiple network simulations with identical parameters.

    Returns:
        List of finalization stats dicts (one per run).

    """
    results = []
    key_order = [TYPES.honest, TYPES.fixed, TYPES.dynamic]
    counts_ordered = [sim_config.node_counts.get(k, 0) for k in key_order]
    node_types = np.fromiter(accumulate(counts_ordered), dtype=int)

    initial_prefs = np.fromiter(
        chain.from_iterable(
            sim_config.initial_preferences.get(k, []) for k in key_order
        ),
        dtype=np.uint8,
    )

    sampler.update_config(
        sample_size=sim_config.snowball.K,
        num_nodes=node_types[-1],
        lnode_start=node_types[-2],
    )

    for _ in trange(sim_config.num_iterations, desc="Running simulations"):
        sim_result = snowball_algo(
            config=sim_config.snowball,
            node_types=node_types,
            initial_preferences=initial_prefs,
            sampler=sampler,
            finality=finality,
        )

        results.append(sim_result)

    return results
