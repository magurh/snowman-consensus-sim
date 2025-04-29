import numpy as np


def slush(
    num_nodes: int,
    num_byz_nodes: int,
    colors: np.ndarray,
    k_slush: int,
    alpha_slush: int,
    num_param_nodes: int,
) -> tuple[int, int]:
    """Centralized Slush protocol implementation."""
    rng = np.random.default_rng()
    num_rounds = 0
    sum_colors = np.sum(colors)

    while True:
        if num_param_nodes > sum_colors or sum_colors > num_nodes - num_param_nodes:
            break

        # Pick a random node that is NOT Byzantine
        random_non_byz_node = rng.integers(num_byz_nodes, num_nodes)

        # Pick a random sample of size k
        random_sample = rng.choice(num_nodes, size=k_slush, replace=False)
        random_sample_decision = np.sum(colors[random_sample])

        if random_sample_decision >= alpha_slush:
            sum_colors = sum_colors - colors[random_non_byz_node] + 1
            colors[random_non_byz_node] = 1
        elif k_slush - random_sample_decision >= alpha_slush:
            sum_colors -= colors[random_non_byz_node]
            colors[random_non_byz_node] = 0

        num_rounds += 1

    final_decision = 1 if sum_colors > num_nodes // 2 else 0
    return final_decision, num_rounds


def weighted_slush(
    num_nodes: int,
    num_byz_nodes: int,
    colors: np.ndarray,
    k_slush: int,
    alpha_slush: float,
    num_param_nodes: int,
    weight_matrix: np.ndarray,
) -> tuple[int, int]:
    """Slush implementation using weighted local aggregation."""
    rng = np.random.default_rng()
    num_rounds = 0
    sum_colors = np.sum(colors)

    while True:
        if num_param_nodes > sum_colors or sum_colors > num_nodes - num_param_nodes:
            break

        random_non_byz_node = rng.integers(num_byz_nodes, num_nodes)
        random_sample = rng.choice(num_nodes, size=k_slush, replace=False)

        weights = weight_matrix[random_sample]
        weighted_sum = np.dot(colors[random_sample], weights)
        random_sample_decision = (k_slush * weighted_sum) / np.sum(weights)

        if random_sample_decision >= alpha_slush:
            sum_colors = sum_colors - colors[random_non_byz_node] + 1
            colors[random_non_byz_node] = 1
        elif k_slush - random_sample_decision >= alpha_slush:
            sum_colors -= colors[random_non_byz_node]
            colors[random_non_byz_node] = 0

        num_rounds += 1

    final_decision = 1 if sum_colors > num_nodes // 2 else 0
    return final_decision, num_rounds
