# P11 — Exact BigZ lower-bound proof and observed native trace refinement

## Mathematical interface

The P7/P10 structured Mojo BigZ search already completed its positive
height-bounded census through B320 using exact sums and independent
Python candidate replay. Its remaining *source-level proof bridge*
is the correspondence between signed arbitrary-precision sum order,
stable pair-record sorting and the first-index binary search.

`formal/lean/BigZLowerBound.lean` instantiates the existing
kernel-checked `SignedLowerBound` theorem over the exact Int sum
projection of structured `(sum,a,b)` records. With a sorted
`List Int` of record sums, the proved lower bound is the **first**
position that is not below the target. It therefore finds an exact
target if and only if some record carries that target, and every
earlier position has a strictly smaller sum. No 64-bit bound appears
in these mathematical statements; repeated equal sums are preserved.

This is **conditional** on the record sums being sorted. The
historical source-level `BigPairIndex.lean` already proves sorting
membership (not compiler equivalence). The compiled native mergesort
and pair comparator are separately checked on synthetic and
real full-census inputs; we do not assert a compiler-level
universal implementation proof.

## Same native BigZ branch with observations

`kernel/bigz_pair_index.mojo` factors its production
`pair_lower_bound` and observable
`trace_pair_lower_bound` through one implementation
`_pair_lower_bound_core`. The optional observer emits

```text
CASE <id> <signed-exact-decimal-target> <array-length>
VAL <signed-exact-decimal-record-sum>
STEP <lo> <hi> <mid> <signed-exact-decimal-pivot>
STOP <first-possible-index>
RESULT <same-index> <membership-bit>
END
```

The observer cannot change branch choice; actual lower-bound code
always compares `BigZ` via the pinned shared `bigz_lt`. A test
compares the traced and untraced return indices for every case.
This instrumentation is **not enabled** in production hot loops;
the nonobserving call still takes the exact same comparison branch.

`kernel/bigz_trace_probe.mojo` emits **18 fixed exact cases**:
empty/single lists, sorted negatives, duplicates, equal-sum plateaus,
signed extremes, values exceeding `2^63` and signed values below
`-2^63`, and values beyond `2^100`. The positive search uses
nonnegative sums, but testing signed extremes exercises the full
underlying BigZ comparator semantics.

`tests/test_bigz_trace.py` independently reconstructs every
midpoint, pivot, branch, first lower-bound index, and exact
membership using Python arbitrary-precision integers, and rejects
deliberately truncated, noncanonical, reordered, and forged cases.

The `formal/lean/BigZTraceReplay.lean` executable then replays the
**same actual native stdout** using mathematical signed Lean Int,
checks every observed state transition against the already
kernel-checked signed lower-bound algorithm, and refuses the same
corrupted transcripts. Unlike the older
`TraceReplay.lean` for the packed Int64 index, it accepts
unbounded canonical signed decimal values.

## Acceptance and reproducibility

```sh
pixi run --locked python tests/test_bigz_trace.py --python-only
bash tools/verify-formal.sh
```

The research Mojo workflow adds compiled Python conformance and
uploads `native-bigz-lower-bound-trace` as an inspectable raw
observation artifact. The formal workflow builds the Lean module,
includes new theorems in the axiom audit, and runs the executable
Lean verifier on the unmodified native trace as well as negative
controls. Existing complete BigZ B320 search, historically pinned
B144/B256/B320 roots, and independent Python full search oracles
remain unchanged.

**Evidence boundary:** kernel-checked proof of signed lower-bound
mathematics + stepwise Lean replay of finite native observations
does **not** imply a whole-program verified Mojo compiler,
authenticated hardware trace, or unbounded fifth-power theorem.
No higher bound or new solution is claimed.
