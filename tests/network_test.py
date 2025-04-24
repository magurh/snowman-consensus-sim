import pytest
import logging

from src.snow.config import SnowballConfig
from src.snow.network import LockstepNetwork, RandomSamplingNetwork
from src.snow.sampler import UniformSampler
from src.snow.node import TYPES

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@pytest.fixture
def simple_config() -> SnowballConfig:
    """Define an instance of SnowballConfig."""
    return SnowballConfig(K=3, AlphaPreference=2, AlphaConfidence=2, Beta=3)


@pytest.fixture
def honest_setup():
    """Setup honest nodes."""
    return {
        TYPES.honest: 20,
    }, {
        TYPES.honest: [0] * 10 + [1] * 10  # split votes
    }

def test_lockstep_round(simple_config, honest_setup):
    """Test lockstep network."""
    node_counts, init_prefs = honest_setup
    net = LockstepNetwork(
        node_counts=node_counts,
        initial_preferences=init_prefs,
        snowball_params=simple_config,
        sampler=UniformSampler(),
    )

    # Check initial distribution and finalization
    assert net._get_distribution() == {0: 10, 1: 10}
    assert net.check_honest_finalization() == False
    assert net.check_partial_finalization() == False

    # Run a single round
    net.run_round()
    logger.info(f"New distribution: {net._get_distribution()}")

def test_lockstep_finalization(simple_config, honest_setup):
    """Test lockstep network finalization."""
    node_counts, init_prefs = honest_setup
    net = LockstepNetwork(
        node_counts=node_counts,
        initial_preferences=init_prefs,
        snowball_params=simple_config,
        sampler=UniformSampler(),
    )

    for _ in range(50):
        if net.check_honest_finalization():
            break
        net.run_round()

    stats = net.get_finalization_stats()
    logger.info(f"Stats: {stats}")

    assert stats["rounds_to_full"] is not None
    assert len(stats["per_node_rounds"]) == 20
    assert sum(stats["distribution"].values()) == 20


def test_random_sampling_finalization(simple_config, honest_setup):
    """Test RandomSamplingNetwork finalization."""
    node_counts, init_prefs = honest_setup
    net = RandomSamplingNetwork(
        node_counts=node_counts,
        initial_preferences=init_prefs,
        snowball_params=simple_config,
        sampler=UniformSampler(),
    )

    for _ in range(500):
        if net.check_honest_finalization():
            break
        net.run_round()

    stats = net.get_finalization_stats()
    logger.info(f"Stats: {stats}")

    assert stats["rounds_to_full"] is not None
    assert len(stats["per_node_rounds"]) == 20
    assert sum(stats["distribution"].values()) == 20
