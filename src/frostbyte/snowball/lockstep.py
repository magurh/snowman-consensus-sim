import numpy as np

from src.config import SnowballConfig
from src.frostbyte.snowball.sampler import SnowballSampler
from src.frostbyte.snowball.state import SnowballState


def snowball_ls(
    config: SnowballConfig,
    node_types: np.ndarray,
    initial_preferences: np.ndarray,
    finality: str = "full",
) -> dict:
    """
    Run centralized Snowball Lockstep with vectorized operations.

    Args:
        config: SnowballConfig instance
        node_types: array [N1, N2, N3] where:
            :0 to N1-1: honest nodes
            :N1 to N2-1: fixed nodes
            :N2 to N3-1: L nodes
        initial_preferences: initial node preferences (0 or 1)
        finality: "full" or "partial" finality

    Returns:
        dictionary with algorithm results

    """
    rng = np.random.default_rng()

    # Save locally number of nodes
    num_honest, num_nodes, lnode_start = (
        node_types[0],
        node_types[-1],
        node_types[-2],
    )

    # LNode responses
    count_0 = np.sum(initial_preferences[:num_honest] == 0)
    lnode_pref = 0 if count_0 < (num_honest - count_0) else 1

    # Initialize SnowballState instance
    state = SnowballState(
        snowball_config=config,
        preferences=initial_preferences.copy(),
        strengths=np.zeros((num_nodes, 2), dtype=np.uint8),
        confidences=np.zeros(num_nodes, dtype=np.uint8),
        last_majority=initial_preferences[:num_honest].copy(),
        finalized=np.zeros(num_nodes, dtype=bool),
        count_0=count_0,
        num_honest=num_honest,
        lnode_pref=lnode_pref,
        finalized_count=0,
    )
    # Initialize sampler
    sampler = SnowballSampler(
        K=config.K,
        num_nodes=num_nodes,
        lnode_start=lnode_start,
        rng=rng,
    )

    rounds, rounds_to_partial = 0, None
    half = num_nodes // 2
    honest_ids = np.arange(num_honest)  # honest indices

    # Run Snowball algorithm
    while True:
        # 1) Partial finality check
        if (state.finalized_count > half) and (rounds_to_partial is None):
            rounds_to_partial = rounds
            if finality == "partial":
                break

        # 2) Check active nodes
        active = honest_ids[~state.finalized[:num_honest]]
        act_size = active.size
        if act_size == 0:
            break

        # 3) Sample K peers without replacement and parse votes
        majority_pref, majority_count = sampler.batch_sampler(
            active,
            state.preferences,
            state.lnode_pref,
        )

        # 4) Update strengths
        pref_pass_mask = majority_count >= config.AlphaPreference

        passed_ids = active[pref_pass_mask]
        passed_prefs = majority_pref[pref_pass_mask]
        state.strengths[passed_ids, passed_prefs] += 1

        # 5) Perform preference changes
        strg_maj = state.strengths[passed_ids, passed_prefs]
        strg_other = state.strengths[passed_ids, 1 - passed_prefs]
        flip_mask = (strg_maj > strg_other) & (
            state.preferences[passed_ids] != passed_prefs
        )

        to_flip = passed_ids[flip_mask]
        new_prefs = passed_prefs[flip_mask]
        state.batch_flip(to_flip, new_prefs)

        # 6) Update confidence counter
        state.batch_confidence_update(active, majority_pref, majority_count)

        rounds += 1

    return {
        "honest_distribution": {0: state.count_0, 1: num_honest - state.count_0},
        "finalized_honest": state.finalized_count,
        "rounds_to_partial": rounds_to_partial,
        "rounds_to_full": rounds if finality == "full" else None,
    }
