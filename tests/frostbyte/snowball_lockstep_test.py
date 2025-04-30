import numpy as np
import pytest
import logging

from src.config import SnowballConfig
from src.frostbyte.snowball import snowball_ls, snowball_rs


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
    result = snowball_ls(config, node_types, initial_prefs, finality="full")
    assert result["honest_distribution"] == {0: 5, 1: 0}
    assert result["finalized_honest"] == 5
    assert result["rounds_to_full"] == 5
    assert result["rounds_to_partial"] == 5

def test_preference_flip(config):
    # Six honest nodes only
    node_types = np.array([6, 6, 6])
    initial_prefs = np.array([0, 0, 0, 1, 0, 1], dtype=np.uint8)
    result = snowball_ls(config, node_types, initial_prefs, finality="full")

    assert result["honest_distribution"] == {0: 6, 1: 0}
    assert result["finalized_honest"] == 6


def test_custom_finalization(config):
    # 7 honest nodes, 2 fixed, 1 Lnode
    node_types = np.array([7, 7, 9])
    initial_prefs = np.array([0, 0, 0, 0, 0, 0, 0, 1, 1], dtype=np.uint8)

    result = snowball_ls(config, node_types, initial_prefs.copy(), finality="full")

    logger.info(f"Rounds to partial: {result['rounds_to_partial']}")
    logger.info(f"Rounds to full: {result['rounds_to_full']}")
    logger.info(f"Honest distribution: {result['honest_distribution']}")

    assert result["honest_distribution"] == {0: 7, 1: 0}
    assert result["finalized_honest"] == 7

# def test_partial_finality_consistency(config, monkeypatch):
#     # seed RNG differently
#     seed = 54321
#     monkeypatch.setattr(np.random, 'default_rng', lambda: np.random.default_rng(seed))

#     node_types = np.array([5, 5, 9])
#     initial_prefs = np.random.randint(0, 2, size=9, dtype=np.uint8)

#     res_ls = snowball_ls(config, node_types, initial_prefs.copy(), finality="partial")
#     res_rs = snowball_rs(config, node_types, initial_prefs.copy(), finality="partial")

#     assert res_ls["rounds_to_partial"] == res_rs["rounds_to_partial"]
