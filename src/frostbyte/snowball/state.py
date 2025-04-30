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
        """Flip single node preference if needed."""
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

    def batch_flip(self, to_flip: np.ndarray, new_prefs: np.ndarray) -> None:
        """
        Flip batch of honest nodes simultaneously.

        Args:
            to_flip: 1D array of honest-node indices to flip
            new_prefs: same-length array of 0/1 majority prefERENCES

        """
        if to_flip.size == 0:
            return

        # Read old preferences
        old = self.preferences[to_flip]

        # Compute net change in count_0:
        #   +1 for each 1<-0,  -1 for each 0<-1
        gain = np.sum((old == 0) & (new_prefs == 1))
        loss = np.sum((old == 1) & (new_prefs == 0))
        self.count_0 += int(gain - loss)

        # Perform the flips
        self.preferences[to_flip] = new_prefs

        # Recompute L-node scalar
        self.curr_lpref = 0 if self.count_0 < (self.num_honest - self.count_0) else 1
