import pytest

from src.config import SnowballConfig
from src.snow.node import FixedNode, LNode, OfflineNode


@pytest.fixture
def config():
    """Define an instance of SnowballConfig."""
    return SnowballConfig(K=3, AlphaPreference=2, AlphaConfidence=2, Beta=3)


def test_offline_node(config):
    """Test offline nodes."""
    node = OfflineNode(
        node_id=0,
        snowball_params=config,
    )
    assert node.finalized is True
    assert node.preference is None
    assert node.on_query(peer_preference=1) is None


def test_fixed_node(config):
    """Test fixed response nodes."""
    node = FixedNode(
        node_id=0,
        fixed_preference=0,
        snowball_params=config,
    )
    assert node.finalized is True
    assert node.preference == 0
    assert node.on_query(peer_preference=1) == 0


def test_lnode_response(config):
    """Test liveness-attacking nodes."""
    node = LNode(
        node_id=0,
        snowball_params=config,
    )
    dist = {0: 70, 1: 30}
    node.update_distribution(dist)

    # Should return 1 (to push towards minority side)
    assert node.on_query(peer_preference=None) == 1

    # Reverse distribution
    node.update_distribution({0: 40, 1: 60})
    assert node.on_query(peer_preference=None) == 0

    # Equal (should return 0 by tie-break rule)
    node.update_distribution({0: 30, 1: 20})
    assert node.on_query(peer_preference=None) == 1
