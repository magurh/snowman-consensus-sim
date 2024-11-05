import numpy as np


def slush(
    num_nodes: int,
    num_byz_nodes: int,
    colors: np.ndarray,
    k_slush: int,
    alpha_slush: int,
    num_param_nodes: int
) -> tuple[int, int]:
    """
    Centralized Slush protocol implementation

    :param num_nodes: number of nodes
    :param num_byz_nodes: number of perfectly Byzantine nodes
    :param colors: 1d array of 0s and 1s
    :param k_slush: Slush protocol parameter
    :param alpha_slush: Slush protocol parameter
    :param num_param_nodes: run algorithm until all but param nodes agree on a state
    
    :return: output of network (0 or 1), number of rounds
    """
    num_rounds = 0
    sum_colors = np.sum(colors)

    while True:
        if num_param_nodes > sum_colors or sum_colors > num_nodes - num_param_nodes:
            # stop when all but num_param_nodes agree on a state
            break

        # Pick a random node that is NOT Byzantine: index >= byz
        random_non_byz_node = np.random.randint(num_byz_nodes, num_nodes)

        # Pick a random sample of size k
        random_sample_decision = np.sum(
            colors[np.random.choice(num_nodes, size=k_slush, replace=False)]
        )
        
        # Compare with threshold parameter
        if random_sample_decision >= alpha_slush:
            # Readjust sum_colors so we don't have to compute from scratch
            sum_colors = sum_colors - colors[random_non_byz_node] + 1
            # Update node color
            colors[random_non_byz_node] = 1
        elif k_slush - random_sample_decision >= alpha_slush:
            sum_colors -= colors[random_non_byz_node]
            colors[random_non_byz_node] = 0

        num_rounds += 1

    random_sample_decision = 1 if sum_colors > num_nodes // 2 else 0
    return random_sample_decision, num_rounds




def weighted_slush(
    num_nodes: int,
    num_byz_nodes: int,
    colors: np.ndarray,
    k_slush: int,
    alpha_slush: np.ndarray,
    num_param_nodes: int,
    weight_matrix: np.ndarray
) -> tuple[int, int]:
    """
    Global Slush protocol implementation using weight matrix for local aggregation

    :param num_nodes: number of nodes
    :param num_byz_nodes: number of perfectly Byzantine nodes
    :param colors: 1d array of 0s and 1s
    :param k_slush: Slush protocol parameter
    :param alpha_slush: Slush protocol parameter
    :param num_param_nodes: run algorithm until all but param nodes agree on a state
    :param weight_matrix: a (num_nodes) array containing weights global w_j to be used in local aggregations

    :return: output of network (0 or 1) and number of rounds taken
    """
    num_rounds = 0
    sum_colors = np.sum(colors)

    while True:
        if num_param_nodes > sum_colors or sum_colors > num_nodes - num_param_nodes:
            break

        # Pick a random node that is NOT Byzantine: index >= byz
        random_non_byz_node = np.random.randint(num_byz_nodes, num_nodes)

        # Pick a random sample of size k
        random_sample = np.random.choice(num_nodes, size=k_slush, replace=False)

        # Compute decision of the sample and rescale
        random_sample_decision = k_slush*np.dot(colors[random_sample], 
                            weight_matrix[random_sample]) / np.sum(weight_matrix[random_sample])

        if random_sample_decision >= alpha_slush:
            # Readjust sum_colors so we don't have to compute from scratch
            sum_colors = sum_colors - colors[random_non_byz_node] + 1
            # Update node color
            colors[random_non_byz_node] = 1
        elif k_slush - random_sample_decision >= alpha_slush:
            # Readjust sum_colors so we don't have to compute from scratch
            sum_colors -= colors[random_non_byz_node]
            # Update node color
            colors[random_non_byz_node] = 0

        num_rounds += 1

    random_sample_decision = 1 if sum_colors > num_nodes // 2 else 0

    return random_sample_decision, num_rounds



