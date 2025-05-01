[![python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)

# Consensus Protocols

The snow gossip protocols are deterministic protocols based on repeated samplings of the network.
We provide two `python` implementations, as follows:

* `snow`: A `python` implementation of the Snow algorithms which mimics a full network of Snow nodes, somewhat similar to the `go` implementation of `go-flare` nodes.
* `frostbyte`: A very fast `numpy` based implementation of the Snow algorithms, which uses a centralized approach with nodes being simple elements of arrays.

The protocols are based on the , described in the [Split Alpha into AlphaPreferences and AlphConfidence](https://github.com/ava-labs/avalanchego/pull/2125) update of the `avalanchego` client.
Namely, the distributed implementation of the Snowball protocoll within our `snow` module can be roughly described as follows:

```bash
def onQuery(peer, peerColor):
  respond(peer, currentColor) // Send our current color to the peer, which might be ⊥
  if currentColor = ⊥:
    currentColor = peerColor // If we do not currently have a color, adopt the peer's color

def snowball():
  confidence = 0
  preferenceStrength = {Red:0, Blue:0}
  while confidence < β:
    if currentColor = ⊥:
      continue // Wait until we hear of a color from a peer

    sampledNodes = sample(N, k) // Sample k nodes from the network
    sampledPreferences = [query(node, currentColor) ∀ node ∈ sampledNodes]
    sampledPreferenceCounts = count(sampledPreferences) // Map each color to the number of times it was sampled
    sampledMajorityColor = argmax(sampledPreferenceCounts)
    if sampledMajorityColor ∉ {Red, Blue}: // The network is still initializing its preferences
      confidence = 0
      continue

    majorityCount = sampledPreferenceCounts[sampledMajorityColor]
    if majorityCount < α:
      confidence = 0 // No one got an alpha majority
      continue

    preferenceStrength[sampledMajorityColor]++
    minorityColor = otherColor(majorityColor)
    if preferenceStrength[majorityColor] > preferenceStrength[minorityColor]:
      currentColor = majorityColor // Update the color we report to other peers

    if majorityColor != lastMajorityColor:
      confidence = 0
    lastMajorityColor = majorityColor
    confidence++
  currentColor = lastMajorityColor
```

## Gossip protocols

The Snow family of consensus protocols is a family of probabilistic gossip protocols first introduced by “Team Rocket” in the [Avalanche whitepaper](https://ipfs.io/ipfs/QmUy4jh5mGNZvLkjies1RWM4YuvJh5o2FYopNPVYwrRVGV) -- see also the [arXiv version](https://arxiv.org/pdf/1906.08936). The family consists of the following gossip protocols:

* Slush
* Snowflake (and it’s slightly modified version Snowflake+)
* Snowball
* Snowman++
* Avalanche

### Slush protocol

The *Slush* protocol is conducted over multiple (possibly asynchronous) communication rounds.
In every round, every node queries a sample (of size *K*) from the set of validators, and asks for the preferred binary state (0 or 1) of each node.
Each node that initiated a query awaits for responses from the sampled nodes, and if a quorum of size *alpha* (for K/2 < alpha <= K) is reached, then the node updates its color to that of the quorum.
The protocol has an additional parameter which tracks the number of queries that each node will make.

### Snowflake protocol

The main limitation of the Slush algorithm is the hard-coded number of rounds, which needs to be quite large to ensure convergence.
*Snowflake* works very similarly to Slush, but here the number of rounds is no longer a node parameter.
Instead, each node maintains a counter, that updates as follows:

* After every state change, the counter resets to 0. (Actually, to 1, since a state change comes with a confidence of 1 in the new state.)
* After a successful query yielding the same supermajority response as the current state (i.e. quorum is reached for a state that coincides with the current preferred state), the counter increases by 1.
* When the counter exceeds a fixed value (*beta* - a new protocol parameter), the node no longer changes its state.

### Snowball protocol

*Snowball* is an improvement on the Snowflake protocol which uses additional confidence counters.
Namely:

* There are now confidence counters for each state, which are updated after every successful query.
* When the confidence in the current state (say 0) becomes lower than that in the opposite state (1), the node updates its state (to 1 in this case).
* If a certain number of consecutive queries (beta) yield the same result, the node no longer changes its state.

### Avalanche protocol

The whitepaper also introduces the Avalanche protocol, which is a consensus protocol that builds on Snowball and uses a Directed Acyclic Graph (DAG) structure.
This non-linear protocol was deployed on the X-chain of the Avalanche network untile the [Cortina update](https://medium.com/avalancheavax/cortina-x-chain-linearization-a1d9305553f6) ([v1.10.0](https://github.com/ava-labs/avalanchego/releases/tag/v1.10.0)).

## Snowman++

Snowman++ is a linear version of Avalanche currently implemented on all Avalanche chains and subnets, as well as on the Flare Networks.
The Snowman++ is a congestion control mechanism available for snowman virtual machines (VMs) -- namely, the protocol introduces a *soft proposer mechanism* which attempts to select a single proposer with the power to issue a block, but opens up block production to every validator if sufficient time has passed without blocks being generated.
(see [Avalanche docs](https://github.com/flare-foundation/go-flare/tree/93fd844b1e85366ee9c1c4a3fb9e9399220534cc/avalanchego/vms/proposervm)).

At a high level, Snowman++ works as follows:

* For each block a small list of validators is randomly sampled, which will act as "proposers" for the next block.
* Each proposer is assigned a submission window: a proposer cannot submit its block before its submission window starts (the block would be deemed invalid), but it can submit its block after its submission window expires, competing with next proposers.
* If no block is produced by the proposers in their submission windows, any validator will be free to propose a block, as happens for ordinary snowman VMs.
