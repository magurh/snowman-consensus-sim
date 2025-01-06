![Go](https://img.shields.io/badge/Golang-1.21.8-%2300ADD8.svg?style=flate&logo=go&logoColor=white)


# Tree Implementation


Snowball's `Tree` implementation uses a modified Patricia tree for deciding on competing blocks.
The tree structure is defined by the binary form of the 32-byte decisions (i.e. block hashes), as shown in the following diagram.

<p align="center">
  <img src="tree.jpg">
</p>

For a single decision, the tree consists of a single block.
When a competing decision is added, the tree branches into two separate directions.
At this point there is no much difference between the naive (`Flat`) implementation and the `Tree` implementation.
These differences become visible when more decisions are added.

Each node of the tree tracks some additional parameters (see `tree.go` for more details):
* Currently Preferred branch
* `DecidedPrefix`: represents the index of the last bit in the prefix that has been decided (i.e., agreed upon by all nodes under this branch).
* `CommonPrefix`: represents the index of the last bit in the prefix that is shared by all nodes under this branch, even if undecided.

When adding a new decision, the tree splits at the first differing bit beyond the `DecidedPrefix`.
This is done using the `FirstDifferenceSubset()` method, defined within `avalanchego/ids/bits.go`.
Note that the counting is done from the most significant bit (MSB) to the least significant bit (LSB) within a byte.
Namely, bit indices are defined as:

[7 6 5 4 3 2 1 0] [15 14 13 12 11 10 9 8] ... [255 254 253 252 251 250 249 248]

where index 7 is the MSB of byte 0.