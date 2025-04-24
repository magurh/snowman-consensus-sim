from collections import Counter
from typing import Any


def summarize_results(results: list[dict]) -> dict[str, Any]:
    """
    Compute summary metrics across multiple simulation results.

    Args:
        results: List of finalization stats (from get_finalization_stats()).

    Returns:
        A summary dictionary with aggregate statistics.

    """
    num_runs = len(results)
    preference_counter: Counter[int] = Counter()
    rounds_to_full: list[int] = []
    rounds_to_partial: list[int] = []
    all_finalization_rounds: list[int] = []

    for res in results:
        dist = res["distribution"]
        preference_counter.update(dist)

        if res["rounds_to_full"] is not None:
            rounds_to_full.append(res["rounds_to_full"])
        if res["rounds_to_partial"] is not None:
            rounds_to_partial.append(res["rounds_to_partial"])

        all_finalization_rounds.extend(res["per_node_rounds"].values())

    return {
        "num_runs": num_runs,
        "final_preference_distribution": dict(preference_counter),
        "avg_rounds_to_full": (
            sum(rounds_to_full) / len(rounds_to_full) if rounds_to_full else None
        ),
        "avg_rounds_to_partial": (
            sum(rounds_to_partial) / len(rounds_to_partial)
            if rounds_to_partial
            else None
        ),
        "avg_per_node_finalization": (
            sum(all_finalization_rounds) / len(all_finalization_rounds)
            if all_finalization_rounds
            else None
        ),
        "min_node_finalization_round": min(all_finalization_rounds, default=None),
        "max_node_finalization_round": max(all_finalization_rounds, default=None),
    }
