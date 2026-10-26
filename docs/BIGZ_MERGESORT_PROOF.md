# P12 — Exact signed BigZ merge-sort: sorted-permutation theorem and native conformance

The mathematical gap after P11 was not lower-bound correctness itself:
that conditional Lean theorem was already established for any sorted
list of arbitrary signed integer sums. What remained was evidence
that the **actual sorted record input** satisfied that hypothesis.

## Mathematical proof

`formal/lean/BigZMergeSort.lean` defines a lexicographic comparator
over `(sum : Int, a : Nat, b : Nat)`, with no machine range bound.
Its component comparisons match the native `bigz_pair_index.mojo`
comparison order: exact sum, a, then b. Lean proves comparator
transitivity and totality, invokes the kernel-checked
`List.pairwise_mergeSort` theorem to establish sorted output and
`List.mergeSort_perm` to establish that every input record is
preserved **with multiplicity**. It proves the sum projection of the
sorted result is nondecreasing, thereby discharging the sortedness
assumption of P11's `bigzRecordLowerBound_correct`. The combined
theorem establishes a correct mathematical first-hit search on the
exact sorted records, including same-sum collision classes.

## Compiled code conformance

`kernel/bigz_sort_probe.mojo` invokes the **same**
`sort_exact_pairs` code as the production native BigZ E5 engine.
Eight deterministic finite cases include empty and single records,
already ordered, reversed, exact duplicate records, multi-limb
positive and negative sums beyond 64 bits, deterministic 64-record
scrambles with duplicate sums, and all 78 positive fifth-power
pair records from bases 1..12. It emits *actual native* full
`IN sum a b` and `OUT sum a b` records; the Python oracle
independently reconstructs every input tuple and checks exact
arbitrary-precision tuple sorting plus all multiplicities. It also
refuses six deliberately corrupted transcripts.

The test is a finite executable conformance check, not a formal
proof that the Mojo compiler implements mathematical `List.mergeSort`
for **every** possible list. The native bottom-up mergesort chooses
the left element on comparator ties, which is a stable merge
operation. When complete key records are identical, stability
cannot be observed from their `(sum,a,b)` fields alone. We claim
sorted permutation and complete collision preservation, not an
independent verified identifier-level tie-stability theorem.

## Trust boundary and execution

The source-level Lean proof closes the mathematical composition
from sorted record construction to certified binary search.
Mojo and Python check representative adversarial generated native
arrays and run the previously verified complete B320 shards again
without changing the search domain, certificates, witnesses or
domain-specific SHA roots. The axiom audit, exact Mojo/Python oracle,
Lean signed BigZ pivot replay, Quint/Apalache and dedicated B320
workflow remain mandatory.

```sh
pixi run --locked python tests/test_bigz_sort.py
bash tools/verify-formal.sh
```

Actual native observations are retained in the
`native-bigz-merge-sort-records` Actions artifact.
A future higher-level machine-semantics project could prove the
Mojo stable bottom-up mergesort itself refines `List.mergeSort` for
all inputs; this P12 component does not claim such a compiler proof.
