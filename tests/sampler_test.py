import pytest

from src.snow.config import SnowballConfig
from src.snow.node import HonestNode
from src.snow.sampler import UniformSampler


def make_dummy_nodes(size: int) -> list[HonestNode]:
    """Create honest nodes with dummy preferences."""
    dummy_config = SnowballConfig(K=3, AlphaPreference=2, AlphaConfidence=2, Beta=3)
    return [
        HonestNode(node_id=i, initial_preference=0, snowball_params=dummy_config)
        for i in range(size)
    ]


def test_sampler_excludes_self():
    """Test sampler excludes self."""
    nodes = make_dummy_nodes(10)
    sampler = UniformSampler()
    target = nodes[3]
    k = 5

    sample = sampler.sample(target, nodes, k)
    sampled_ids = {n.node_id for n in sample}

    assert target.node_id not in sampled_ids, "Sampler should not return self."
    assert len(sampled_ids) == k, "Sampler should return exactly k nodes."


def test_sampler_unique():
    """Test sampled nodes are unique."""
    nodes = make_dummy_nodes(20)
    sampler = UniformSampler()
    target = nodes[0]

    sample = sampler.sample(target, nodes, 10)
    ids = [n.node_id for n in sample]
    assert len(set(ids)) == len(ids), "Sampled nodes must be unique."


def test_sampler_all():
    """Test all nodes can be sampled."""
    nodes = make_dummy_nodes(6)
    sampler = UniformSampler()
    target = nodes[2]

    # We should be able to sample all others except the target node.
    sample = sampler.sample(target, nodes, 5)
    sampled_ids = {n.node_id for n in sample}
    assert target.node_id not in sampled_ids
    assert len(sampled_ids) == 5


def test_sampler_invalid():
    """Test invalid sample size."""
    nodes = make_dummy_nodes(5)
    sampler = UniformSampler()
    target = nodes[1]

    with pytest.raises(ValueError):
        sampler.sample(target, nodes, 5)
