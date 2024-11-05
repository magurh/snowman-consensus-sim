import random

class Node:
    def __init__(self, node_id, initial_state, sample_size):
        self.node_id = node_id
        self.preferred_state = initial_state  # Initial preferred state (0 or 1)
        self.confidence = 0                   # Confidence counter
        self.finalized = False                # Finalized status
        self.sample_size = sample_size
    
    def sample_network(self, network):
        """Samples a subset of nodes from the network."""
        return random.sample([node for node in network if node != self], self.sample_size)
