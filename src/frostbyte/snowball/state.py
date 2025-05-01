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
    last_majority: np.ndarray
    finalized: np.ndarray
    count_0: int
    num_honest: int
    lnode_pref: int
    finalized_count: int

    def honest_flip(self, node_id: int, majority_pref: int) -> None:
        """Flip single node preference if needed."""
        other = 1 - majority_pref

        # Only flip if this pref strength strictly exceeds the other.
        if (self.preferences[node_id] != majority_pref) and (
            self.strengths[node_id, majority_pref] > self.strengths[node_id, other]
        ):
            # Flip the honest node
            self.preferences[node_id] = majority_pref
            # Adjust zero count
            self.count_0 += +1 if majority_pref == 0 else -1
            # Recompute LNode scalar
            self.lnode_pref = (
                0 if self.count_0 < (self.num_honest - self.count_0) else 1
            )

    def confidence_update(
        self,
        node_id: int,
        maj_count: int,
        maj_pref: int,
    ) -> None:
        """
        Update confidence parameter and finalize single node.

        Confidence increased if:
          1) maj_count >= alpha_conf, and
          2) maj_pref == old preferences

        Args:
            node_id: current node
            maj_count: sampled majority count
            maj_pref: sampled majority pref

        """
        # If majority is below AlphaConfidence, reset confidence
        if maj_count < self.snowball_config.AlphaConfidence:
            self.confidences[node_id] = 0
            return

        # If majority above AlphaConfidence, check if majority repeated
        if self.last_majority[node_id] != maj_pref:
            # If not, reset confidence parameter (to 1)
            self.confidences[node_id] = 1
        else:
            # If so, increase confidence parameter
            self.confidences[node_id] += 1

            # Check if node can finalize
            if self.confidences[node_id] >= self.snowball_config.Beta:
                self.finalized[node_id] = True
                self.finalized_count += 1

        # Update last majority for the next round
        self.last_majority[node_id] = maj_pref

    def batch_flip(self, to_flip: np.ndarray, new_prefs: np.ndarray) -> None:
        """
        Flip batch of honest nodes simultaneously.

        Args:
            to_flip: 1D array of honest-node indices to flip
            new_prefs: same-length array of 0/1 majority preferences

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

        # Perform the flips
        self.preferences[to_flip] = new_prefs

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
        # Build mask of who really confirms the color
        confirm_mask = (maj_count >= self.snowball_config.AlphaConfidence) & (
            maj_pref == self.last_majority[active]
        )

        # Bump only the survivors
        survivors = active[confirm_mask]
        self.confidences[survivors] += 1

        non_survivors = np.setdiff1d(active, survivors, assume_unique=True)
        self.confidences[non_survivors] = 1

        # Finalize anyone who just Beta in confidence
        to_finalize = survivors[
            self.confidences[survivors] >= self.snowball_config.Beta
        ]
        self.finalized[to_finalize] = True
        self.finalized_count += len(to_finalize)

        # Update last_majority for all active
        self.last_majority[active] = maj_pref
