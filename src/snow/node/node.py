from collections import defaultdict
from typing import override

from src.snow.config import SnowballConfig

from .base import BaseNode
from .type import TYPES


class HonestNode(BaseNode):
    """Honest node that follows the Snowball consensus protocol."""

    def __init__(
        self,
        node_id: int,
        initial_preference: int | None,
        snowball_params: SnowballConfig,
    ) -> None:
        """Initialize an honest node."""
        super().__init__(node_id, initial_preference, snowball_params)
        self.confidence: int = 0
        self.preference_strength: dict[int, int] = defaultdict(int)
        self.last_majority: int | None = None
        self.type: str = TYPES.honest

    @override
    def on_query(self, peer_preference: int | None) -> int | None:
        """
        Respond with this node's current preference.

        Args:
            peer_preference (Optional[int]): The querying peer's preference.

        Returns:
            Optional[int]: This node's current preference.

        """
        if self.preference is None:
            self.preference = peer_preference
            return None  # previous preference

        return self.preference

    def snowball_round(
        self,
        sampled_preferences: list[int | None],
    ) -> None:
        """
        Execute one round of the Snowball protocol.

        Args:
            sampled_preferences: List of preferences sampled.

        """
        if self.finalized or self.preference is None:
            return

        vote_counts: dict[int, int] = defaultdict(int)
        for pref in sampled_preferences:
            if pref is not None:
                vote_counts[pref] += 1

        if not vote_counts:
            self.confidence = 0
            return

        majority_pref = max(vote_counts, key=vote_counts.get)
        majority_count = vote_counts[majority_pref]

        if majority_count < self.snowball_params.AlphaPreference:
            self.confidence = 0
            return

        self.preference_strength[majority_pref] += 1
        other = 1 - majority_pref if majority_pref in [0, 1] else None

        if (
            other is not None
            and self.preference_strength[majority_pref]
            > self.preference_strength[other]
        ):
            self.preference = majority_pref

        if majority_count < self.snowball_params.AlphaConfidence:
            self.confidence = 0
            return

        if self.last_majority != majority_pref:
            self.confidence = 0
        else:
            self.confidence += 1

        self.last_majority = majority_pref

        if self.confidence >= self.snowball_params.Beta:
            self.finalized = True
