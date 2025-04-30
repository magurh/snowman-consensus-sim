import numpy as np

from src.config import SnowballConfig

from .sampler import SnowballSampler
from .state import SnowballState


def snowball_rs(
    config: SnowballConfig,
    node_types: np.ndarray,
    initial_preferences: np.ndarray,
    finality: str = "full",
) -> dict:
    """
    Run centralized Snowball Random Sampling with vectorized operations.

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
    num_honest, num_nodes, lnode_start = node_types[0], node_types[-1], node_types[-2]

    # Set up arrays for describing nodes
    preferences = initial_preferences.copy()
    confidences = np.zeros(num_nodes, dtype=np.uint8)
    finalized = np.zeros(num_nodes, dtype=bool)
    strengths = np.zeros((num_nodes, 2), dtype=np.uint8)
    count_0 = np.sum(preferences[:num_honest] == 0)

    # LNode responses
    curr_lpref = 0 if count_0 < (num_honest - count_0) else 1

    # Bundle data into a SnowballState
    state = SnowballState(
        preferences=preferences,
        strengths=strengths,
        count_0=count_0,
        num_honest=num_honest,
        curr_lpref=curr_lpref,
    )
    # Initialize sampler
    sampler = SnowballSampler(
        K=config.K,
        num_nodes=num_nodes,
        lnode_start=lnode_start,
        rng=rng,
    )

    rounds, rounds_to_partial = 0, None

    # Run Snowball algorithm
    while True:
        # Select honest unfinished nodes
        active = np.where(~finalized[:num_honest])[0]

        if active.size == 0:
            break  # full honest finalization reached

        # If only partial finalization is sought:
        if finalized[:num_honest].sum() > num_nodes // 2 and rounds_to_partial is None:
            rounds_to_partial = rounds
            if finality == "partial":
                # Break if network is partially finalized
                break

        for node_id in active:
            # Sample network and parse responses
            zeros, ones = sampler.sample_and_count(
                node_id,
                state.preferences,
                state.curr_lpref,
            )

            if max(zeros, ones) < config.AlphaPreference:
                confidences[node_id] = 0
                continue

            majority_pref = 1 if ones > zeros else 0
            state.strengths[node_id, majority_pref] += 1

            # Update network preferences and distribution
            state.honest_flip(
                node_id,
                majority_pref,
            )

            if max(zeros, ones) < config.AlphaConfidence:
                confidences[node_id] = 0
                continue

            # Update confidence
            confidences[node_id] += 1

            if confidences[node_id] >= config.Beta:
                finalized[node_id] = True

        rounds += 1

    return {
        "honest_distribution": {
            0: state.count_0,
            1: num_honest - state.count_0,
        },
        "finalized_honest": int(np.sum(finalized[:num_honest])),
        "rounds_to_partial": rounds_to_partial,
        "rounds_to_full": rounds if finality == "full" else None,
    }
