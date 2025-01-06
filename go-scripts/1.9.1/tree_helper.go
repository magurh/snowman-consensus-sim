// Copyright (C) 2019-2022, Ava Labs, Inc. All rights reserved.
// See the file LICENSE for licensing terms.

package snowball

import (
	"fmt"

	"github.com/ava-labs/avalanchego/ids"
)


func (u *unaryNode) CommonPrefix() int { return u.commonPrefix }
func (u *unaryNode) GetChild() node { return u.child }

// NodeMetrics holds the fields we want to record from each node
type NodeMetrics struct {
    DecidedPrefix       int
    CommonPrefix        int
    Confidence          string
}

type TreeChildren struct {
    Node              node     // The actual node (unaryNode or binaryNode)
	ParentAddress     string
    Preference        ids.ID   // The node's preferred choice
    DecidedPrefix     int      // The number of decided bits in the prefix
    CommonPrefix	  int      // The number of bits shared in the common prefix (for unaryNode)
}


// AllConfidences traverses the entire Tree from the root,
// returning a map from "node's preference ID" to NodeMetrics.
// If multiple nodes share the same preference ID, the last visited overwrites.
func (t *Tree) AllConfidences() map[ids.ID]NodeMetrics {
    results := make(map[ids.ID]NodeMetrics)
    if t.node == nil {
        return results
    }

    var traverse func(n node)
    traverse = func(n node) {
        // Attempt to type-assert the node to *unaryNode
        un, ok := n.(*unaryNode)
        if ok {
            // 1) The node's preference
            id := un.Preference() // This is the node interface's .Preference() method

            // 2) The node's decided prefix (# of bits decided)
            decidedPrefix := un.DecidedPrefix()

            // 3) This node's commonPrefix (unaryNode-specific field)
            commonPrefix := un.CommonPrefix()

            // 4) The node's Snowball counters:
            //    un.snowball is unarySnowball, which embeds unarySnowflake
            //    so .Confidence() is a method from unarySnowflake
            conf := un.snowball.String()

            results[id] = NodeMetrics{
                DecidedPrefix:      decidedPrefix,
                CommonPrefix:       commonPrefix,
                Confidence:         conf,
            }
        }

        // Get child nodes from n.Printable()
        _, childNodes := n.Printable()
        for _, child := range childNodes {
            traverse(child)
        }
    }

    traverse(t.node)
    return results
}


func (t *Tree) AllChildren() map[string]TreeChildren {
    results := make(map[string]TreeChildren)
    if t.node == nil {
        return results
    }

    var traverse func(n node, parentAddr string)
    traverse = func(n node, parentAddr string) {
        if n == nil {
            return
        }

        // Use memory address as the key
        address := fmt.Sprintf("%p", n)

        if un, ok := n.(*unaryNode); ok {
            results[address] = TreeChildren{
                Node:          un,
                ParentAddress: parentAddr,
                Preference:    un.Preference(),
                DecidedPrefix: un.DecidedPrefix(),
                CommonPrefix:  un.CommonPrefix(),
            }
            traverse(un.child, address)
        } else if bn, ok := n.(*binaryNode); ok {
            results[address] = TreeChildren{
                Node:          bn,
                ParentAddress: parentAddr,
                Preference:    bn.Preference(),
                DecidedPrefix: bn.DecidedPrefix(),
                CommonPrefix:  -1, // binaryNode doesn't have CommonPrefix
            }
            for _, child := range bn.children {
                traverse(child, address)
            }
        }
    }

    traverse(t.node, "")
    return results
}

