package snowball_test

import (
    "fmt"
    "strings"
    "testing"

    "github.com/ava-labs/avalanchego/ids"
    "github.com/ava-labs/avalanchego/snow/consensus/snowball"
)

// idToBinary is just a helper to visualize ID bytes.
func idToBinary(id ids.ID) string {
    bytes := id[:]
    var binaryStrings []string
    for _, b := range bytes {
        binaryStrings = append(binaryStrings, fmt.Sprintf("%08b", b))
    }
    return strings.Join(binaryStrings, "")
}

// TestTreeVisualization shows how you can:
//  - Initialize a Tree
//  - Add multiple decisions
//  - Submit polls (some with majority, some without)
//  - Observe how the tree evolves (using tree.String())
func TestTreeVisualization(t *testing.T) {
    // 1. Define Snowball parameters.
    //    Adjust these as desired. K is the sample size, Alpha is the majority threshold,
    //    and BetaVirtuous/BetaRogue are the confidence thresholds.
    params := snowball.Parameters{
        K:            3, // number of samples (not heavily used in this simple test)
        Alpha:        2, // minimum votes to potentially switch preference
        BetaVirtuous: 2, // confidence threshold for virtuous decisions
        BetaRogue:    3, // confidence threshold for rogue decisions
    }

    // 2. Initialize the Tree with an initial preference (root).
    tree := snowball.Tree{}
    initialPreference := ids.GenerateTestID()
    tree.Initialize(params, initialPreference)
    fmt.Printf("Initialized Tree with Root Preference: %s\nBinary: %s\n\n",
        initialPreference.String()[:6], idToBinary(initialPreference)[:6])

    // We'll keep track of these IDs to print confidence later
    var decisionIDs []ids.ID
    decisionIDs = append(decisionIDs, initialPreference)

    // 3. Add some competing decisions to the Tree.
    for i := 0; i < 3; i++ {
        newID := ids.GenerateTestID()
        decisionIDs = append(decisionIDs, newID)
        tree.Add(newID)
    }
    for _, id := range decisionIDs {
        tree.Add(id)
        fmt.Printf("Added Decision: %s\nBinary: %s\n", id, idToBinary(id)[:6])
    }
    fmt.Println()
    fmt.Println(tree.String()) // Print the tree structure
    fmt.Println()
    // 4. Prepare a series of polls. Each poll is an ids.Bag that indicates
    //    how many votes each decision received in that round.
    //
    //    - First poll is a near-tie but still a majority for decisionIDs[0].
    //    - Second poll is *split* between decisionIDs[1] and [2] (no strong majority).
    //    - Third poll strongly favors decisionIDs[3].
    //    - Fourth poll gives a slight majority to decisionIDs[3], etc.
    //    You can adapt these as you wish.
    polls := []ids.Bag{
        func() ids.Bag {
            b := ids.Bag{}
            b.AddCount(decisionIDs[1], 2) // majority for ID[1]
            b.AddCount(decisionIDs[2], 1)
            return b
        }(),
        func() ids.Bag {
            b := ids.Bag{}
            // This poll is split 1 vote each for ID[1] and ID[2].
            // Possibly not enough to force a preference change.
            b.AddCount(decisionIDs[1], 1)
            b.AddCount(decisionIDs[2], 1)
            return b
        }(),
        func() ids.Bag {
            b := ids.Bag{}
            // Strong majority for ID[2]
            b.AddCount(decisionIDs[3], 3)
            return b
        }(),
        func() ids.Bag {
            b := ids.Bag{}
            // Slight majority for ID[3], re-affirming ID[3]
            b.AddCount(decisionIDs[3], 2)
            b.AddCount(decisionIDs[2], 1)
            return b
        }(),
    }

    // Print current preference
    pref := idToBinary(tree.Preference())
    fmt.Printf("Before polling: Current Preference = %s\n", pref[:6])

    // After each poll round:
    confMap := tree.AllConfidences()
    fmt.Println("Current Node Confidences:")
    for id, metrics := range confMap {
        fmt.Printf("- ID=%s | decidedPrefix=%d | commonPrefix=%d | ",
            idToBinary(id)[:6], 
            metrics.DecidedPrefix,
            metrics.CommonPrefix,
        )
        fmt.Printf(metrics.Confidence)
        fmt.Println()
    }
    fmt.Println()

    // 5. Simulate polling rounds and observe how the tree evolves.
    for round, poll := range polls {
        fmt.Printf("Round %d:\n", round+1)
        for _, id := range poll.List() {
            fmt.Printf("  Polling result -> %s : %d votes\n", idToBinary(id)[:6], poll.Count(id))
        }
        // Record the poll in the tree
        tree.RecordPoll(poll)
        
        // Print the current top-level Preference after this round
        pref := idToBinary(tree.Preference())
        fmt.Printf("After Round %d: Current Preference = %s\n", round+1, pref[:6])

        // After each poll round:
        confMap := tree.AllConfidences()
        fmt.Println("Current Node Confidences:")
        for id, metrics := range confMap {
            fmt.Printf("- ID=%s | decidedPrefix=%d | commonPrefix=%d | ",
                idToBinary(id)[:6], 
                metrics.DecidedPrefix,
                metrics.CommonPrefix,
            )
            fmt.Printf(metrics.Confidence)
            fmt.Println()
        }
        fmt.Println()

        // 6. Optionally check if the Tree has become finalized.
        if tree.Finalized() {
            fmt.Printf("Tree finalized on preference: %s\nBinary: %s\n\n",
                tree.Preference(), idToBinary(tree.Preference())[:6])
            break
        }
    }

    // 7. Final check if we ended without finalization.
    if !tree.Finalized() {
        fmt.Println("Tree is not yet finalized after all rounds.")
        fmt.Printf("Current Preference: %s\n\n", idToBinary(tree.Preference())[:6])
    }

}

