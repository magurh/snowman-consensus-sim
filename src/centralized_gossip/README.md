# Gossip Protocols

## Efficient gossiping

A very efficient way of simulating certain gossip protocols is a "centralized" approach, where all nodes are assumed to be identical and are thus simply modelled as elements of an array. Note that this assumption is valid for the Slush protocol as no confidence counters are used. Additionally, the network is assumed to be fully connected.

A similar approach was used in the [Consensus Learning](https://arxiv.org/abs/2402.16157) simulations.