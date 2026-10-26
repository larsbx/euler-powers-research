# P10 — Complete 2..320 native Mojo BigZ height coverage

## Actual computation versus a proposed plan

The standalone workflow `.github/workflows/bigz-full-range.yml`
compiles the pinned **Mojo** BigZ pair-index search and executes the
full 80-shard plan covering all ordered target heights
`2 <= e <= 320`. The other positive E5 constraints remain
`1 <= a <= b <= c <= d < e`, with primitive GCD=1, and the
partitioning modulus is `M=35`. Shards each contain at most four
consecutive heights and independently honor CPU, memory, output and
60-second wall-clock per-shard caps.

The plan, signed-free rational-free arithmetic and receipt controller
come from the prior P7/P8 implementation. Before any shard can count
toward a *complete* acceptance, every line of the actual native Mojo
stdout is compared with a separate exhaustive exact Python map of
all candidate fifth-power pairs and positive right pairs **without
relying on the production 99000 modular sieve**. The controller
requires exact source and dependency pins, complete contiguous
height coverage, fresh-scope retry tickets and canonical receipts.
SHA-256 binds data integrity but does not authenticate remote workers.

`BigShardCoverage.lean` now proves the fixed **80-shard** plan is
contiguous, covers every target height from 2 through 320, and
respects the maximum four-height range restriction. These are
mathematical facts about the plan, not a universal proof that the
Mojo compiler implements a correct search.

## Cross-language and historical-root acceptance

`tests/reconcile_bigz_b320.py` takes only accepted actual native
transcripts, not reconstructed Python ones. It validates the entire
plan, then assembles three independently replayed canonical
`E5PARTv1` domain views:

| Prefix | Canonical partitions | Required historical comparison |
| --- | ---: | --- |
| B144 | 2,574 | All previous pinned PART rows, stream SHA-256 and replay root `5b8ed68d8512bb11bf4ac57e2f79657e65893427c157c0615b784d86671af482` |
| B256 | 4,590 | Independent Python exact search, 2,664,481 positive-complement visits and replay root `157fdbc83048ddc782d8aa04c9691d0c34dabfaf96819a6976dd6671e284e07e` |
| B320 | 5,742 | Every PART/CERT was separately checked in the 80 shard oracles; generates a **new** domain-specific root from actual native output |

Each view must retain only the known primitive positive witness
`(27,84,110,133,144)`. No new positive solution in this bounded
domain is asserted **until the new hosted run has passed**. The
B320 root is generated and recorded in
`bigz-b320-crosscheck.json`, not guessed.

The tested `replay_partition.py` accepts B320 because it is a
mathematical verifier of reconstructed E5PARTv1 evidence, not an
attempt to run the historical packed Int64 search at B320. The
existing B144/B256 packed execution limits are unchanged.

## Reproduce

```sh
pixi run --locked verify
pixi run --locked python tools/bigz_shard_plan.py execute \
  --bound 320 --width 4 --modulus 35 \
  --output benchmarks/results/bigz-shards-b320
pixi run --locked python tools/bigz_shard_plan.py verify \
  --output benchmarks/results/bigz-shards-b320
pixi run --locked python tests/reconcile_bigz_b320.py \
  benchmarks/results/bigz-shards-b320 \
  --output benchmarks/results/bigz-b320-crosscheck.json
```

The dedicated hosted workflow includes a whole-process GNU time
resource report and preserves each native transcript, all acceptance
receipts, the exact root crosscheck JSON, and the resource log as
`exact-bigz-height-shards-B320`.

This is a **finite exhaustive computation subject to separately
verified algorithm and execution evidence**, not a proof of arbitrary
unbounded E5 completeness, new algebraic families, or reproduction
of historical million-height claims. Expanding beyond 320 requires
fresh resource, proof, and domain reviews.
