from collections.abc import Callable

from src.node.adversary import FixedNode, LNode, OfflineNode
from src.node.base import BaseNode
from src.node.honest import HonestNode
from src.node.type import TYPES
from src.snow.config import SnowballConfig


def _raise_pref_error(msg: str) -> None:
    raise ValueError(msg)


_NODE_CONSTRUCTORS: dict[str, Callable[[int, int | None, SnowballConfig], BaseNode]] = {
    TYPES.honest: lambda i, p, c: HonestNode(i, p, c),
    TYPES.fixed: lambda i, p, c: FixedNode(
        i,
        p if p is not None else _raise_pref_error("Fixed node must have a preference."),
        c,
    ),
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
