from collections.abc import Callable

from src.config import SnowballConfig

from .adversary import FixedNode, LNode, OfflineNode
from .base import BaseNode
from .node import HonestNode
from .type import TYPES


def _generate_fixed_node(i: int, p: int | None, c: SnowballConfig) -> BaseNode:
    if p is None:
        e = "Fixed node must have a preference."
        raise ValueError(e)
    return FixedNode(i, p, c)


_NODE_CONSTRUCTORS: dict[str, Callable[[int, int | None, SnowballConfig], BaseNode]] = {
    TYPES.honest: lambda i, p, c: HonestNode(i, p, c),
    TYPES.fixed: _generate_fixed_node,
    TYPES.offline: lambda i, _, c: OfflineNode(i, c),
    TYPES.dynamic: lambda i, _, c: LNode(i, c),
}


def make_node(
    node_type: str, node_id: int, preference: int | None, config: SnowballConfig
) -> BaseNode:
    """
    Construct a node of the given type using registered constructors.

    Args:
        node_type: A string from TYPES.
        node_id: Unique node identifier.
        preference: Initial preference (0, 1, or None).
        config: Shared Snowball protocol parameters.

    Returns:
        A BaseNode instance.

    """
    try:
        constructor = _NODE_CONSTRUCTORS[node_type]
        return constructor(node_id, preference, config)
    except KeyError:
        supported = list(_NODE_CONSTRUCTORS.keys())
        msg = f"Unknown node type: {node_type}. Supported types: {supported}"
        raise ValueError(msg) from None
