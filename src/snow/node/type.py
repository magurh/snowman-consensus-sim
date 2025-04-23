from dataclasses import dataclass


@dataclass
class NodeType:
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
