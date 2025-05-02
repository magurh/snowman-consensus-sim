import numpy as np
import pandas as pd

from src.config import SimConfig, SnowballConfig
from src.frostbyte.sampler import SnowballSampler
from src.frostbyte.simul import run_snowball
from src.frostbyte.snowball import snowball_ls
from src.snow.node import TYPES


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

    sampler = SnowballSampler(rng=np.random.default_rng())

    rows: list[dict[str, int]] = []

    for alpha in range(11, 22):
        sim_config.update_snowball(AlphaConfidence=alpha)
        results = run_snowball(
            sim_config=sim_config,
            sampler=sampler,
            snowball_algo=snowball_ls,
            finality="full",
        )
        results["AlphaConfidence"] = alpha
        rows.append(results)

    _df = pd.DataFrame(rows)
    _df.to_csv("snowball_sims.csv", index=False)


if __name__ == "__main__":
    start()
