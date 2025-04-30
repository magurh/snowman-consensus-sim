from dataclasses import dataclass

import numpy as np


@dataclass
class SnowballState:
    """Holds all the mutable Snowball state."""

    preferences: np.ndarray
    strengths: np.ndarray
    count_0: int
    num_honest: int
    curr_lpref: int

    def honest_flip(self, node_id: int, majority_pref: int) -> None:
        """Flip node preference (in-place) if needed."""
        other = 1 - majority_pref

        # Only flip if this pref strength strictly exceeds the other.
        if self.strengths[node_id, majority_pref] > self.strengths[node_id, other]:
            old = int(self.preferences[node_id])
            if old != majority_pref:
                # Flip the honest node
                self.preferences[node_id] = majority_pref
                # Adjust zero count
                self.count_0 += -1 if old == 0 else +1

        # Recompute LNode scalar
        self.curr_lpref = 0 if self.count_0 < (self.num_honest - self.count_0) else 1
