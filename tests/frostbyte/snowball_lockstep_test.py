import logging

import numpy as np
import pytest

from src.config import SnowballConfig
from src.frostbyte.sampler import SnowballSampler
from src.frostbyte.snowball import snowball_ls


@pytest.fixture
def config():
    """Define an instance of SnowballConfig."""
    return SnowballConfig(K=3, AlphaPreference=3, AlphaConfidence=3, Beta=5)


@pytest.fixture
def sampler():
    """Define an instance of SnowballSampler."""
    return SnowballSampler(rng=np.random.default_rng())


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def test_basic_termination(config, sampler):
    # Five honest nodes only
    node_types = np.array([5, 5, 5])
    initial_prefs = np.array([0, 0, 0, 0, 0], dtype=np.uint8)

    sampler.update_config(
        sample_size=config.K,
        num_nodes=node_types[-1],
        lnode_start=node_types[-2],
    )
    result = snowball_ls(
        config=config,
        node_types=node_types,
        initial_preferences=initial_prefs,
        sampler=sampler,
        finality="full",
    )

    assert result["honest_0"] == 5
    assert result["honest_1"] == 0
    assert result["finalized_honest"] == 5
    assert result["rounds_to_full"] == 5
    assert result["rounds_to_partial"] == 5


def test_preference_flip(config, sampler):
    # Six honest nodes only
    node_types = np.array([6, 6, 6])
    initial_prefs = np.array([0, 0, 0, 0, 1, 1], dtype=np.uint8)

    sampler.update_config(
        sample_size=config.K,
        num_nodes=node_types[-1],
        lnode_start=node_types[-2],
    )
    result = snowball_ls(
        config=config,
        node_types=node_types,
        initial_preferences=initial_prefs,
        sampler=sampler,
        finality="full",
    )

    assert result["honest_0"] == 6
    assert result["honest_1"] == 0
    assert result["finalized_honest"] == 6


def test_custom_finalization(config, sampler):
    # 7 honest nodes, 2 fixed, 1 Lnode
    node_types = np.array([7, 7, 9])
    initial_prefs = np.array([0, 0, 0, 0, 0, 0, 0, 1, 1], dtype=np.uint8)

    sampler.update_config(
        sample_size=config.K,
        num_nodes=node_types[-1],
        lnode_start=node_types[-2],
    )
    result = snowball_ls(
        config=config,
        node_types=node_types,
        initial_preferences=initial_prefs,
        sampler=sampler,
        finality="full",
    )

    logger.info(f"Rounds to partial: {result['rounds_to_partial']}")
    logger.info(f"Rounds to full: {result['rounds_to_full']}")

    assert result["honest_0"] == 7
    assert result["honest_1"] == 0
    assert result["finalized_honest"] == 7
