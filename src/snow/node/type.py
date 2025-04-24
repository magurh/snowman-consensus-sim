from dataclasses import dataclass


@dataclass
class NodeType:
    """Tracker for all types of nodes."""

    honest: str
    offline: str
    fixed: str
    dynamic: str


TYPES = NodeType(
    honest="honest",
    offline="offline",
    fixed="fixed",
    dynamic="Lnode",
)
