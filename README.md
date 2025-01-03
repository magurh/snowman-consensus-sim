![Go](https://img.shields.io/badge/Golang-1.21.8-%2300ADD8.svg?style=flate&logo=go&logoColor=white)


# avalanchego v.1.9.x

## Snowball Consensus

The Snowball consensus has two distinct implementations:

* `Flat` implementation: this is the naive implementation described the original whitepaper, which relies on repeated sampling of the network.
Votes are directly counted for each color, and decisions are independent of each other.
Practically, this is a direct wrapper of a `nnarySnowball` logic, which works as follows:
	1. Sample the network.
	2. Get current preferences from the sample.
	3. Update preference and confidence counter according to Snowball logic -- if new value becomes preference, confidence resets to 1.
	4. Repeat steps 1-3 until confidence reaches the `beta` parameter.
 
* `Tree` implementation: this implementation is optimized for handling complex dependencies between different decision choices in the consensus algorithm.
In this way, the Snowball instance is implemented using a modified Patricia tree, i.e. using a hierarchical structure.
Each node of this tree corresponds to a decision point (a proposed block).
Practically, the `Tree` implementation builds on the `unarySnowball` logic, using `unaryNodes` to manage preferences hierarchically.



