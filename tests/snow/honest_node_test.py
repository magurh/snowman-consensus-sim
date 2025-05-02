import numpy as np
import pytest

from src.config import SnowballConfig
from src.snow.node import HonestNode


@pytest.fixture
def config():
    """Define an instance of SnowballConfig."""
    return SnowballConfig(K=3, AlphaPreference=2, AlphaConfidence=2, Beta=3)


def test_on_query_uninitialized(config):
    """Test on_query response with preference=None."""
    node = HonestNode(
        node_id=0,
        initial_preference=None,
        snowball_params=config,
    )
    response = node.on_query(1)
    assert node.preference == 1
    assert response is None


def test_on_query_initialized(config):
    """Test on_query response with preference."""
    node = HonestNode(
        node_id=0,
        initial_preference=1,
        snowball_params=config,
    )
    response = node.on_query(0)
    assert response == 1
    assert node.preference == 1


def test_unsuccessful_query(config):
    """Test unsuccessful queries."""
    node = HonestNode(
        node_id=0,
        initial_preference=0,
        snowball_params=config,
    )
    # Only one vote for 1, not enough for AlphaPreference
    node.snowball_round(np.array([1, None, None], dtype=object))
    assert node.confidence == 0
    assert node.preference == 0
    assert node.finalized is False


def test_finalization(config):
    """Test successful finalization in binary case."""
    node = HonestNode(
        node_id=0,
        initial_preference=0,
        snowball_params=config,
    )

    for _ in range(3):  # Needs Beta = 3 rounds
        node.snowball_round(np.array([1, 1, 1], dtype=object))

    assert node.preference == 1
    assert node.confidence == 3
    assert node.finalized is True


def test_preference_switch(config):
    """Test preference switch."""
    node = HonestNode(
        node_id=0,
        initial_preference=0,
        snowball_params=config,
    )

    # First: 2 rounds of majority = 1
    node.snowball_round(np.array([1, 1, 1], dtype=object))
    node.snowball_round(np.array([1, 1, 1], dtype=object))

    # Then: 1 round where 0 dominates
    node.snowball_round(np.array([0, 0, 0], dtype=object))

    # preference_strength[1] = 2, [0] = 1 → should still stick with 1
    assert node.preference == 1
