import numpy as np

from src.config import SnowballConfig
from src.frostbyte.sampler import SnowballSampler
from src.frostbyte.snowball.state import SnowballState


def snowball_rs(
    config: SnowballConfig,
    node_types: np.ndarray,
    initial_preferences: np.ndarray,
    sampler: SnowballSampler,
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
        sampler: SnowballSampler config
        finality: "full" or "partial" finality

    Returns:
        dictionary with algorithm results

    """
    # Save locally number of nodes
    num_honest, num_nodes = (
        node_types[0],
        node_types[-1],
    )

    # LNode responses
    count_0 = np.sum(initial_preferences[:num_honest] == 0)
    lnode_pref = 0 if count_0 < (num_honest - count_0) else 1

    # Bundle data into a SnowballState
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

    # Check sampler configuration
    sampler.check_config()

    rounds, rounds_to_partial = 0, None

    # Run Snowball algorithm
    while True:
        # Select honest unfinished nodes
        active = np.where(~state.finalized[:num_honest])[0]
        if active.size == 0:
            break  # full honest finalization reached

        # If only partial finalization is sought:
        if state.finalized_count > num_nodes // 2 and rounds_to_partial is None:
            rounds_to_partial = rounds
            if finality == "partial":
                # Break if network is partially finalized
                break

        # Choose node, sample network, and parse responses
        node_id = sampler.choose_node(active)
        majority_pref, majority_count = sampler.sample_and_count(
            node_id,
            state.preferences,
            state.lnode_pref,
        )

        if majority_count < config.AlphaPreference:
            state.confidences[node_id] = 0
            continue

        state.strengths[node_id, majority_pref] += 1

        # Update network preferences and distribution
        state.honest_flip(
            node_id,
            majority_pref,
        )

        state.confidence_update(
            node_id,
            majority_count,
            majority_pref,
        )

        rounds += 1

    return {
        "honest_0": state.count_0,
        "honest_1": num_honest - state.count_0,
        "finalized_honest": state.finalized_count,
        "rounds_to_partial": rounds_to_partial,
        "rounds_to_full": rounds if finality == "full" else None,
    }
