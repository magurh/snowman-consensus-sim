import numpy as np

from src.config import SnowballConfig
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

    # Set up arrays for describing nodes
    preferences = initial_preferences.copy()
    confidences = np.zeros(num_nodes, dtype=np.uint8)
    finalized = np.zeros(num_nodes, dtype=bool)
    strengths = np.zeros((num_nodes, 2), dtype=np.uint8)
    count_0 = np.sum(preferences[:num_honest] == 0)

    # LNode responses
    lnode_pref = 0 if count_0 < (num_honest - count_0) else 1
    preferences[lnode_start:] = lnode_pref

    # Initialize SnowballState instance
    state = SnowballState(
        snowball_config=config,
        preferences=preferences,
        strengths=strengths,
        confidences=confidences,
        finalized=finalized,
        count_0=count_0,
        num_honest=num_honest,
        lnode_pref=lnode_pref,
        finalized_count=0,
    )

    rounds, rounds_to_partial = 0, None
    half = num_nodes // 2
    honest_ids = np.arange(num_honest)  # honest indices

    # Run Snowball algorithm
    while True:
        # 1) Partial finality check
        if state.finalized_count > half:
            if rounds_to_partial is None:
                rounds_to_partial = rounds
            if finality == "partial":
                break

        # 2) Check active nodes
        active = honest_ids[~state.finalized[:num_honest]]
        act_size = active.size
        if act_size == 0:
            break

        # 3) Sample K peers without replacement for each active node
        peer_samples = np.empty((act_size, config.K), dtype=int)

        for idx, node_id in enumerate(active):
            # draw K distinct peers from [0..N-2]
            u = rng.choice(num_nodes - 1, size=config.K, replace=False)
            # shift those ≥ node_id up by 1 to skip self
            peer_samples[idx] = u + (u >= node_id)

        # 4) Gather their preferences
        sampled_prefs = preferences[peer_samples]  # shape (M, K)

        # 5) Count zeros/ones
        ones = sampled_prefs.sum(axis=1).astype(int)
        zeros = config.K - ones

        # 6) Alpha Preference stage
        majority_pref = (ones > zeros).astype(np.uint8)
        majority_count = np.where(ones > zeros, ones, zeros)
        pref_pass_mask = majority_count >= config.AlphaPreference

        # 7) Update strengths for those that pass
        passed_ids = active[pref_pass_mask]
        passed_prefs = majority_pref[pref_pass_mask]
        strengths[passed_ids, passed_prefs] += 1

        # 8) Check honest node flips
        strg_maj = strengths[passed_ids, passed_prefs]
        strg_other = strengths[passed_ids, 1 - passed_prefs]
        flip_mask = (strg_maj > strg_other) & (preferences[passed_ids] != passed_prefs)

        # 9) Apply honest flips
        to_flip = passed_ids[flip_mask]
        new_prefs = passed_prefs[flip_mask]
        state.batch_flip(to_flip, new_prefs)

        # 10) Update confidence:
        state.batch_confidence_update(active, majority_pref, majority_count)

        rounds += 1

    return {
        "honest_distribution": {0: state.count_0, 1: num_honest - state.count_0},
        "finalized_honest": int(finalized[:num_honest].sum()),
        "rounds_to_partial": rounds_to_partial,
        "rounds_to_full": rounds if finality == "full" else None,
    }
