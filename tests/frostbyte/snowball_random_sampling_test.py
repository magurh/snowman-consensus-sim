import numpy as np
import pytest
import logging

from src.config import SnowballConfig
from src.frostbyte.snowball import snowball_rs


@pytest.fixture
def config():
    """Define an instance of SnowballConfig."""
    return SnowballConfig(K=3, AlphaPreference=2, AlphaConfidence=2, Beta=5)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def test_basic_termination(config):
    # Five honest nodes only
    node_types = np.array([5, 5, 5])
    initial_prefs = np.array([0, 0, 0, 0, 0], dtype=np.uint8)
    result = snowball_rs(config, node_types, initial_prefs, finality="full")
    assert result["honest_distribution"] == {0: 5, 1: 0}
    assert result["finalized_honest"] == 5
    assert result["rounds_to_full"] == 25
    assert result["rounds_to_partial"] >= 15

def test_preference_flip(config):
    # Five honest nodes only
    node_types = np.array([5, 5, 5])
    initial_prefs = np.array([0, 0, 0, 0, 1], dtype=np.uint8)
    result = snowball_rs(config, node_types, initial_prefs, finality="full")

    assert result["honest_distribution"] == {0: 5, 1: 0}
    assert result["finalized_honest"] == 5
    assert result["rounds_to_full"] == 25
    assert result["rounds_to_partial"] >= 15


def test_custom_finalization(config):
    # 7 honest nodes, 0 fixed, 1 Lnodes
    node_types = np.array([7, 7, 8])
    initial_prefs = np.array([0, 0, 0, 0, 0, 0, 0, 1], dtype=np.uint8)

    result = snowball_rs(config, node_types, initial_prefs.copy(), finality="full")

    logger.info(f"Rounds to partial: {result['rounds_to_partial']}")
    logger.info(f"Rounds to full: {result['rounds_to_full']}")
    logger.info(f"Honest distribution: {result['honest_distribution']}")

    assert result["honest_distribution"] == {0: 7, 1: 0}
    assert result["finalized_honest"] == 7
