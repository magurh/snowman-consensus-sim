import numpy as np

from src.config import SnowballConfig

from .state import SnowballState


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
    curr_lpref = 0 if count_0 < (num_honest - count_0) else 1
    preferences[lnode_start:] = curr_lpref

    # Initialize SnowballState instance
    state = SnowballState(
        preferences=preferences,
        strengths=strengths,
        count_0=count_0,
        num_honest=num_honest,
        curr_lpref=curr_lpref,
    )

    rounds, rounds_to_partial = 0, None
    half = num_nodes // 2
    node_ids = np.arange(num_honest)  # honest indices

    # Run Snowball algorithm
    while True:
        # 1) Partial finality check
        fin_count = int(finalized[:num_honest].sum())
        if fin_count > half:
            if rounds_to_partial is None:
                rounds_to_partial = rounds
            if finality == "partial":
                break

        # 2) Check active nodes
        active = node_ids[~finalized[:num_honest]]
        act_size = active.size
        if act_size == 0:
            break

        # 3) Sample K peers in batch for each active node
        u = rng.integers(0, num_nodes - 1, size=(act_size, config.K))
        rows = active[:, None]
        sampled = u + (u >= rows)

        # 4) Gather their preferences
        sampled_prefs = preferences[sampled]  # shape (M, K)

        # 5) Count zeros/ones
        ones = sampled_prefs.sum(axis=1).astype(int)
        zeros = config.K - ones

        # 6) Alpha Preference stage
        maj_pref = (ones > zeros).astype(np.uint8)
        maj_count = np.where(ones > zeros, ones, zeros)
        ok_pref_mask = maj_count >= config.AlphaPreference

        # 7) Update strengths for those that pass
        idx = active[ok_pref_mask]
        mp = maj_pref[ok_pref_mask]
        strengths[idx, mp] += 1

        # 8) Check honest node flips
        strg_maj = strengths[idx, mp]
        strg_other = strengths[idx, 1 - mp]
        flip_mask = strg_maj > strg_other

        # 9) Apply honest flips
        state.batch_flip(idx[flip_mask], mp[flip_mask])

        # 10) Alpha Confidence stage confidence reset
        ok_conf_mask = maj_count >= config.AlphaConfidence
        # Reset those who fail, increment those who pass
        confidences[active[~ok_conf_mask]] = 0
        pass_conf = active[ok_conf_mask]
        confidences[pass_conf] += 1

        # 11) finalize any whose confidence >= Beta
        just_fin = confidences[pass_conf] >= config.Beta
        finalized[pass_conf[just_fin]] = True

        rounds += 1

    return {
        "honest_distribution": {0: count_0, 1: num_honest - count_0},
        "finalized_honest": int(finalized[:num_honest].sum()),
        "rounds_to_partial": rounds_to_partial,
        "rounds_to_full": rounds if finality == "full" else None,
    }
