# P8 — Gap-free BigZ height plans and independently replayed receipts

The P7 **Mojo** arithmetic stays in `kernel/bigz_pair_index.mojo`
and `kernel/bigz_shard.mojo`. P8 adds a deterministic Python control
plane (`tools/bigz_shard_plan.py`) to run the actual compiled Mojo
worker and admit a complete finite height interval only after exact
independent replay. The orchestration is not a substitute for Mojo
arithmetic or a new numerical oracle inside the worker.

## Exact plan scope

A plan declares the **complete** closed set of positive target heights
`{2,3,...,B}`, with `2<=B<=320`, partition modulus
`2<=M<=35`, and `1<=shard_width<=4`. Intervals are computed in
ascending order with `[2, min(2+w-1,B)]` and successor-adjacent
boundaries. The validator rejects a missing, repeated, reordered,
overlapping, over-wide or extra interval, and it requires the final
height to equal the requested B. Different plans can never reuse one
another's receipts.

The mathematical `BigShardCoverage.lean` module proves that the
small `2..12` and `2..16` fixture plans cover all declared heights,
with valid width, and rejects gap, overlap, missing-tail and excess
fixture intervals. It instantiates the existing general
`ShardPlan.contiguousPlan_covers` theorem. These proofs concern the
**plan**, not the success or completeness of any compiled worker.

## Execution authority, retry and failure behavior

The control plane compiles the real pinned native
`kernel/bigz_shard.mojo` with the locked `finite-math-kernels`
dependency. Before building it verifies both the exact dependency Git
HEAD and a clean tracked/untracked working tree; otherwise it refuses
to attribute evidence to that pinned source. It invokes one worker
process per finite interval.
On Linux each invocation is constrained by CPU seconds, address
space (`RLIMIT_AS`), output size (`RLIMIT_FSIZE`) and wall-clock
timeout. The default contract is 60 seconds, 4096 MiB, and 1 MiB
transcript per four-height shard; operator-selected overrides remain
inside hard configuration caps. Compilation has a separate 180-second
timeout.

The written **plan** commits to its exact sorted intervals,
`kernel/bigz_shard.mojo` and `kernel/bigz_pair_index.mojo`
source SHA-256, the `kernel/euler_exact.mojo` fifth-power/GCD
adapter SHA-256, the exact independent Python verifier source
SHA-256, the immutable upstream `finite-math-kernels` Git
commit in `scripts/run_mojo.sh`, and `pixi.lock` SHA-256.

A shard transitions through scoped, monotonically increasing
attempt tickets (at most three), native execution, full independent
verification, and then a content-addressed receipt. A failure leaves
an explicit abort record and an unaccepted attempt, **never** a
success receipt. Restarting the same plan may retry it under a
new ticket; an interrupted transcript that was already validated
may be independently replayed before its receipt is committed.
A present but corrupted receipt or wrong source/scope fails closed.

After executing all declared intervals, the verifier:
- Requires both exact raw Mojo stdout and its canonical JSON receipt.
- Compares every line, PART counter, certificate and total against an
  independently enumerated Python exact-fifth-power pair multimap.
- Recomputes every per-shard SHA-256, plan SHA-256 and source identity.
- Refuses missing or altered intervals, transcripts, counts, duplicate
  cross-shard witnesses, or stale/corrupted receipts.
- Writes `accepted.json` **only after** every shard has passed.

All JSON uses sorted keys, minimal separators and one terminal LF.
The accepted manifest lists the exact bounded scope, each receipt's
SHA-256, total positive-complement visits and observed witnesses.
SHA-256 protects integrity relative to the manifest; it **does not
authenticate a remote worker, establish fresh execution, or prove a
compiler correct**. The source-level Lean proof and separate Python
exhaustive per-shard oracle provide distinct evidence.

## Reproducible commands

```sh
pixi run --locked verify-research
pixi run --locked python tests/test_bigz_plan.py
pixi run --locked python tools/bigz_shard_plan.py plan \
  --bound 12 --width 4 --modulus 35 --output benchmarks/results/bigz-shards-b12
pixi run --locked python tools/bigz_shard_plan.py execute \
  --bound 12 --width 4 --modulus 35 --output benchmarks/results/bigz-shards-b12
pixi run --locked python tools/bigz_shard_plan.py verify \
  --output benchmarks/results/bigz-shards-b12
```

The [P9 full B144 native BigZ reconciliation](BIGZ_B144_CROSSCHECK.md)
checks every target height through 144 against both a per-shard exact
Python oracle and historical independent packed-index certificates.

The CI lane additionally runs `tests/test_bigz_plan_native.py`.
It executes and verifies real native shards covering **every target
height 2..12**, checks deterministic receipt reuse, and deliberately
mutates a transcript and removes a tail shard to prove refusal. All
accepted native evidence is uploaded as the
`exact-bigz-height-shards-B12` artifact.

A complete `2..320` plan is **constructible** but is not treated as
an accepted `2..320` census until all 80 width-four shards have
actually executed and independently passed. The tests at isolated
heights near 320 remain *shard specimens*, not a complete search.
No new primitive solution, infinite-family theorem or reproduction of
historical published large-range claims is implied.

## Remaining research obligations

The newly created receipts bind to repository sources and the pinned
library but are not cryptographically signed machine attestations.
Multi-host acceptance needs a separate signed challenge, verifier
identity and commit-before-execute authority contract. Optimization
for larger B requires bounded memory profiling, incremental/reusable
BigZ indices and full-shard deterministic scheduling, while strictly
separating completed finite height coverage from larger conjectures.
