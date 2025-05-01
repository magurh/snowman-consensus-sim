from dataclasses import dataclass

import numpy as np

from src.config import SnowballConfig


@dataclass
class SnowballState:
    """Holds all the mutable Snowball state."""

    snowball_config: SnowballConfig
    preferences: np.ndarray
    strengths: np.ndarray
    confidences: np.ndarray
    finalized: np.ndarray
    count_0: int
    num_honest: int
    lnode_pref: int
    finalized_count: int

    def honest_flip(self, node_id: int, majority_pref: int) -> bool:
        """Flip single node preference if needed."""
        other = 1 - majority_pref
        flipped = False

        # Only flip if this pref strength strictly exceeds the other.
        if self.strengths[node_id, majority_pref] > self.strengths[node_id, other]:
            old = int(self.preferences[node_id])
            if old != majority_pref:
                # Flip the honest node
                self.preferences[node_id] = majority_pref
                # Adjust zero count
                self.count_0 += -1 if old == 0 else +1
                # Update flag
                flipped = True
                # Recompute LNode scalar
                self.lnode_pref = 0 if self.count_0 < (self.num_honest - self.count_0) else 1

        return flipped

    def confidence_update(
        self,
        node_id: int,
        maj_count: int,
        flipped: bool,
    ) -> None:
        """
        Update confidence parameter and finalize single node.

        Confidence increased if:
          1) maj_count >= alpha_conf, and
          2) maj_pref == old preferences (flipped == True)

        Args:
            node_id: current node
            maj_pref: sampled majority preference
            maj_count: sampled majority count
            flipped: bool indicating whether state flipped

        """
        if maj_count < self.snowball_config.AlphaConfidence:
            self.confidences[node_id] = 0
            return

        if flipped:
            self.confidences[node_id] = 1
        else:
            self.confidences[node_id] += 1
            if self.confidences[node_id] >= self.snowball_config.Beta:
                self.finalized[node_id] = True
                self.finalized_count += 1

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
        gain = int(np.sum((old == 1) & (new_prefs == 0)))  # zeros gained
        loss = int(np.sum((old == 0) & (new_prefs == 1)))  # zeros lost
        self.count_0 += int(gain - loss)

        # Perform the flips and reset confidences
        self.preferences[to_flip] = new_prefs
        self.confidences[to_flip] = 0

        # Recompute L-node scalar
        self.lnode_pref = 0 if self.count_0 < (self.num_honest - self.count_0) else 1

    def batch_confidence_update(
        self,
        active: np.ndarray,
        maj_pref: np.ndarray,
        maj_count: np.ndarray,
    ) -> None:
        """
        Update confidence parameters and finalize nodes.

        Confidence increased if:
          1) maj_count[i] >= alpha_conf, and
          2) maj_pref[i] == self.preferences[node]

        Args:
            active: array of active nodes
            maj_pref: array of sampled majority preference
            maj_count: array of sampled majority counts

        """
        # Grab the current honest-node preferences
        current_prefs = self.preferences[active]
        # Build mask of who really confirms the color
        confirm_mask = (maj_count >= self.snowball_config.AlphaConfidence) & (
            maj_pref == current_prefs
        )

        # Reset all failures
        self.confidences[active[~confirm_mask]] = 0

        # Bump only the survivors
        survivors = active[confirm_mask]
        self.confidences[survivors] += 1

        # Finalize anyone who just Beta in confidence
        finalized_mask = self.confidences[survivors] >= self.snowball_config.Beta
        self.finalized[survivors[finalized_mask]] = True

        self.finalized_count += int(finalized_mask[: self.num_honest].sum())
