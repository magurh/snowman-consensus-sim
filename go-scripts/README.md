![Go](https://img.shields.io/badge/Golang-1.21.8-%2300ADD8.svg?style=flate&logo=go&logoColor=white)


# go scripts

This subdirectory contains version controlled go-scripts for testing `go-flare` nodes.

## v1.9.0

As of v1.9.0, the consensus parameters are listed in the config file `go-flare/avalanchego/config/flags.go`.
The values used in the protocol are the ones suggested in the original [Avalanche paper](https://ipfs.io/ipfs/QmUy4jh5mGNZvLkjies1RWM4YuvJh5o2FYopNPVYwrRVGV).
The relevant configurable parameters are set below:

```bash
	// Consensus
fs.Int(SnowSampleSizeKey, 20, "Number of nodes to query for each network poll")
fs.Int(SnowQuorumSizeKey, 15, "Alpha value to use for required number positive results")
fs.Int(SnowVirtuousCommitThresholdKey, 15, "Beta value to use for virtuous transactions")
fs.Int(SnowRogueCommitThresholdKey, 20, "Beta value to use for rogue transactions")
fs.Int(SnowAvalancheNumParentsKey, 5, "Number of vertexes for reference from each new vertex")
fs.Int(SnowAvalancheBatchSizeKey, 30, "Number of operations to batch in each new vertex")
fs.Int(SnowConcurrentRepollsKey, 4, "Minimum number of concurrent polls for finalizing consensus")
fs.Int(SnowOptimalProcessingKey, 50, "Optimal number of processing containers in consensus")
fs.Int(SnowMaxProcessingKey, 1024, "Maximum number of processing items to be considered healthy")
fs.Duration(SnowMaxTimeProcessingKey, 2*time.Minute, "Maximum amount of time an item should be processing and still be healthy")
fs.Uint(SnowMixedQueryNumPushVdrKey, 10, fmt.Sprintf("If this node is a validator, when a container is inserted into consensus, send a Push Query to %s validators and a Pull Query to the others. Must be <= k.", SnowMixedQueryNumPushVdrKey))
fs.Uint(SnowMixedQueryNumPushNonVdrKey, 0, fmt.Sprintf("If this node is not a validator, when a container is inserted into consensus, send a Push Query to %s validators and a Pull Query to the others. Must be <= k.", SnowMixedQueryNumPushNonVdrKey))
```

A more detailed description of these parameters can be found in the [avalanche docs](https://github.com/ava-labs/avalanche-docs/blob/732354e5f04b799c8ace23a37e10073b6b8a242f/content/docs/api-reference/avalanche-go-configs-flags.mdx#L777):

* `--snow-concurrent-repolls (int)?`: Snow consensus requires repolling transactions that are issued during low time of network usage.
This parameter lets one define how aggressive the client will be in finalizing these pending transactions.
This should only be changed after careful consideration of the tradeoffs of Snow consensus.
The value must be at least 1 and at most --snow-rogue-commit-threshold.
Defaults to 4.

* `--snow-sample-size (int)?`: Snow consensus defines k as the number of validators that are sampled during each network poll.
This parameter lets one define the k value used for consensus.
his should only be changed after careful consideration of the tradeoffs of Snow consensus.
The value must be at least 1.
Defaults to 20.

* `--snow-quorum-size (int)?`: Snow consensus defines alpha as the number of validators that must prefer a transaction during each network poll to increase the confidence in the transaction.
This parameter lets us define the alpha value used for consensus.
This should only be changed after careful consideration of the tradeoffs of Snow consensus.
The value must be at greater than k/2.
Defaults to 15.

* `--snow-virtuous-commit-threshold (int)?`: Snow consensus defines beta1 as the number of consecutive polls that a virtuous transaction must increase its confidence for it to be accepted.
This parameter lets us define the beta1 value used for consensus.
This should only be changed after careful consideration of the tradeoffs of Snow consensus.
The value must be at least 1.
Defaults to 15.

* `--snow-rogue-commit-threshold (int)?`: Snow consensus defines beta2 as the number of consecutive polls that a rogue transaction must increase its confidence for it to be accepted.
This parameter lets us define the beta2 value used for consensus.
This should only be changed after careful consideration of the tradeoffs of Snow consensus.
The value must be at least beta1.
Defaults to 20.

* `--snow-optimal-processing (int)`?: Optimal number of processing items in consensus.
The value must be at least 1.
Defaults to 50.

* `--snow-max-processing (int)?`: Maximum number of processing items to be considered healthy.
Reports unhealthy if more than this number of items are outstanding.
The value must be at least 1. 
Defaults to 1024.

* `--snow-max-time-processing (duration)?`: Maximum amount of time an item should be processing and still be healthy.
Reports unhealthy if there is an item processing for longer than this duration.
The value must be greater than 0.
Defaults to 2m.


These parameters are referred throughout the repository as follows (imported in `go-flare/avalanchego/config/config.go` using `getCOnsensusConfig()` method):

```bash
func getConsensusConfig(v *viper.Viper) avalanche.Parameters {
	return avalanche.Parameters{
		Parameters: snowball.Parameters{
			K:                       v.GetInt(SnowSampleSizeKey),
			Alpha:                   v.GetInt(SnowQuorumSizeKey),
			BetaVirtuous:            v.GetInt(SnowVirtuousCommitThresholdKey),
			BetaRogue:               v.GetInt(SnowRogueCommitThresholdKey),
			ConcurrentRepolls:       v.GetInt(SnowConcurrentRepollsKey),
			OptimalProcessing:       v.GetInt(SnowOptimalProcessingKey),
			MaxOutstandingItems:     v.GetInt(SnowMaxProcessingKey),
			MaxItemProcessingTime:   v.GetDuration(SnowMaxTimeProcessingKey),
			MixedQueryNumPushVdr:    int(v.GetUint(SnowMixedQueryNumPushVdrKey)),
			MixedQueryNumPushNonVdr: int(v.GetUint(SnowMixedQueryNumPushNonVdrKey)),
		},
		BatchSize: v.GetInt(SnowAvalancheBatchSizeKey),
		Parents:   v.GetInt(SnowAvalancheNumParentsKey),
	}
}
```

More details about these parameters can be found in the `Snowflake` structs:
* `beta` - number of consecutive successful queries required for finalization.
* `confidence` - number of successful polls in a row that have returned the preference
* `finalized` – A bool that prevents the state from changing after the required number of consecutive polls has been reached.

Note: The practical implementation includes two `beta` parameters, `betaVirtuous` (or `beta1`) and `betaRogue` (or `beta2`).
If there are no known conflicts with an operation, the state can be accepted with a snowflake counter of `betaVirtuous`.
Otherwise, a `betaRogue` value is required.
