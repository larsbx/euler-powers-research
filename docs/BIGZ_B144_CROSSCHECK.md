# P9 — Complete positive BigZ height coverage through B=144

## Two independent numerical implementations

P8 accepted only the small complete B12 plan; P7 exercised isolated
heights near 320. This milestone executes the **entire** contiguous
positive E5 domain 2 <= e <= 144 in the native structured BigZ Mojo
worker, without using the bounded packed-index worker as the execution
engine.

The plan is deterministic, 36 adjacent height shards of width at most 4
with M=35. The source-level Lean `bigzPlan144_valid`,
`bigzPlan144_width`, and `bigzPlan144_covers` theorems establish
the corresponding finite partition coverage and per-shard width.
The Python controller separately verifies that the actual plan has
exactly these intervals, current source pins, and no missing or extra
accepted records.

Each native BigZ shard is constrained to 60 seconds, 4,096 MiB of
address space, and 1 MiB of output; subprocess execution is bounded
by a wall-clock timeout. Its raw Mojo stdout is independently
re-enumerated by Python using exact fifth powers and all ordered pairs
**without using the production 99000 modular prefilter**. Every PART
row, positive right-pair visit, certificate and footer must match
before a shard receipt is committed.

## Historical agreement as a second check

`tests/reconcile_bigz_b144.py` requires a fully accepted 2..144
BigZ plan, reads only the **actual raw native shard transcripts** and
reassembles their canonical PART/CERT rows into the earlier E5PARTv1
domain. It compares them against the immutable historical fixture
`certificates/pair_partition_e144_m35.json`, then recomputes the
original per-key SHA-256 leaf/root and canonical-stream digest.

The expected checked quantities are:

| Quantity | Historical B144/M35 reference |
| --- | --- |
| Declared target heights | Every height from 2 through 144 |
| Adjacent BigZ shards | 36 |
| Canonical PART rows | 2,574 |
| Strictly positive-complement visits | 475,063 |
| Primitive strictly positive certificates | 1 |
| Witness | (27, 84, 110, 133, 144) |
| E5PART-REPLAY-v2 root | `5b8ed68d8512bb11bf4ac57e2f79657e65893427c157c0615b784d86671af482` |
| E5PART-STREAM-v1 canonical digest | `62048fc9a3cfaaf4b3ba8e451cf9c7d3b8343ee250c87ad516aae69197166645` |

The two algorithms are meaningfully different: one sorts the older
fixed-radix Int64 packed index and one sorts structured BigZ records;
the independent Python oracle constructs hash maps of arbitrary-
precision integers. Agreement across the finite B144 workload is
strong bounded evidence, **not** a universal proof of compiled
algorithm correctness or a claim about heights beyond 144.

## Reproduce and evidence

The pinned hosted Mojo workflow executes all 36 native BigZ shards,
verifies every receipt, and runs the historical reconciliation.
The complete raw stdout, scoped receipts, full accepted manifest,
new crosscheck JSON, and GNU time resource report are preserved
together as `exact-bigz-height-shards-B144` in GitHub Actions.

```sh
pixi run --locked python tools/bigz_shard_plan.py execute \
  --bound 144 --width 4 --modulus 35 --output benchmarks/results/bigz-shards-b144
pixi run --locked python tools/bigz_shard_plan.py verify \
  --output benchmarks/results/bigz-shards-b144
pixi run --locked python tests/reconcile_bigz_b144.py \
  benchmarks/results/bigz-shards-b144 \
  --output benchmarks/results/bigz-b144-crosscheck.json
```

A failed, interrupted, stale, partially executed, extra, overlapping
or tampered plan cannot be promoted to the complete accepted
B144 record. Hashes bind integrity relative to repository sources,
not remote worker identity or cryptographic freshness. B256 and B320
whole-range BigZ coverage remain **unaccepted** until all their own
height shards have actually executed and passed independent replay.
No new primitive solution, extrapolated million-height result, or
open-conjecture proof is asserted here.
