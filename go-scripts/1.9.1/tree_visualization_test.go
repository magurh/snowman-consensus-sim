package snowball_test

import (
    "fmt"
    "testing"

    "github.com/ava-labs/avalanchego/ids"
    "github.com/ava-labs/avalanchego/snow/consensus/snowball"
)


func TestAllChildren(t *testing.T) {
    params := snowball.Parameters{
        K:            5,
        Alpha:        3,
        BetaVirtuous: 2,
        BetaRogue:    4,
    }
    tree := snowball.Tree{}
    initialPreference := ids.GenerateTestID()
    tree.Initialize(params, initialPreference)

    fmt.Printf("Initial decision: %s  Binary: %s\n", initialPreference.String()[:6], idToBinary(initialPreference)[:6])

    for i := 0; i < 3; i++ {
        newID := ids.GenerateTestID()
        tree.Add(newID)
        fmt.Printf("Added Decision: %s Binary: %s\n", newID.String()[:6], idToBinary(newID)[:6])
    }
    fmt.Println()

    children := tree.AllChildren()
    for addr, child := range children {
        fmt.Printf("Node: %s, Parent Node: %s, Preference: %s, DecidedPrefix: %d, CommonPrefix: %d\n",
            addr,
            child.ParentAddress,
            idToBinary(child.Preference)[:6],
            child.DecidedPrefix,
            child.CommonPrefix,
        )
    }
}
