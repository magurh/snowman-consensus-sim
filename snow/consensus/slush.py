import random

from snow.node.node import Node
from snow.node.network import Network


class SlushNode(Node):
    def __init__(self, node_id, initial_state, sample_size, quorum):
        super().__init__(node_id, initial_state, sample_size)
        self.quorum = quorum  
    
    def update_state(self, sampled_states):
        """Updates the node's preferred state if the sampled majority meets the quorum."""
        if self.finalized:
            return
        
        # Count occurrences of each state in the sampled nodes
        state_counts = {state: sampled_states.count(state) for state in set(sampled_states)}
        
        # Determine the majority state if it meets quorum
        majority_state, count = max(state_counts.items(), key=lambda item: item[1])
        
        if count >= self.quorum:
            self.preferred_state = majority_state



class SlushNetwork(Network):
    def __init__(self, nodes):
        super().__init__(nodes)  # Initialize the base Network class

    @classmethod
    def initialize_network(cls, num_nodes, initial_states, sample_size, quorum):
        """
        Creates and initializes a Slush network of nodes with given configuration.
        """
        nodes = [SlushNode(node_id=i, initial_state=initial_states[i], sample_size=sample_size, quorum=quorum) for i in range(num_nodes)]
        return cls(nodes)

