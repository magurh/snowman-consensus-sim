![Go](https://img.shields.io/badge/Golang-1.21.8-%2300ADD8.svg?style=flate&logo=go&logoColor=white)


# avalanchego v.1.9.x

## Snowball Consensus Implementation

The Snowball consensus has two distinct implementations:

* `Flat` implementation: this is the naive implementation described the original whitepaper, which relies on repeated sampling of the network.
Votes are directly counted for each color, and decisions are independent of each other.
Practically, this is a direct wrapper of a `nnarySnowball` logic, which works as follows:
	1. Sample the network.
	2. Get current preferences from the sample.
	3. Update preference and confidence counter according to Snowball logic -- if new value becomes preference, confidence resets to 1.
	4. Repeat steps 1-3 until confidence reaches the `beta` parameter.
 
* `Tree` implementation: while the simple `Flat` implementation uses a repeated sampling to find a winning color in a set of possible choices, the `Tree` implementation extends this logic by allowing each color to be a node in a branching data structure. 
This uses modified Patricia tree, where each node has its own confidence counter, thus using a hierarchical structure.
Practically, the `Tree` implementation builds on the `unarySnowball` logic, using `unaryNodes` to manage preferences hierarchically.
Note that if a node's confidence reaches `beta`, the protocol prunes sibling branches and locks in that node's branch.
This process continues until a single branch is considered final.


Ultimately, the `Tree` Snowball implementation in `snowball/tree.go` is specialized to handle multi-branch conflicts elegantly by modeling them as a hierarchy rather than trying to track every color in a `Flat` structure.
This optimizes the process of merging/pruning and keeps the consensus process efficient.

