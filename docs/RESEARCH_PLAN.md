# Proof obligations and research stages

## P0 — Certified baseline

- Check the four published primitive integer examples by exact integer arithmetic and gcd.
- Maintain positive-only counts separately from signed-solution counts.
- Document original papers, subsequent search ranges, and whether coverage is exhaustive or partial.
- Keep source metadata (including version/date of preprints).

## P1 — Finite-ring obstruction program

- Derive admissible fifth-power residue sets for \(p^k\) and selected composite moduli.
- Turn any universal congruence assertion into a short proof or a finite check with auditable source, modulus, and exact search completeness.
- Analyze CRT combinations without asserting unwarranted independence.
- Seek genuinely new necessary conditions beyond the modulo-11 and modulo-25 lemmas.

**Deliverable:** machine-reproducible residue tables plus human-readable certified lemmas.

### P1 prime-power and CRT milestone

The [prime-power ring and CRT suite](PRIME_POWER_CRT.md) now evaluates
fifth powers over complete finite rings Z/p^kZ with the pinned shared
`finite-math-kernels` arithmetic and an independent Python oracle.
Lean proves modular left-pair prefilter soundness for all positive
primitive solutions. Measured runtime pruning is deliberately deferred:
no production census behavior or bounded certificate is changed.

## P2 — Geometric structure

- Catalog known rational lines, curves, and higher-dimensional special loci of \(X_5\).
- Distinguish positive real intersections from cancellation loci.
- Seek rational curves with infinitely many rational points in the positive region.
- Investigate whether rational-point density is obstructed by arithmetic geometry.

**Deliverable:** a classified list with existence and positivity proofs, or precise obstructions.

## P3 — Near-cancellation arithmetic

Study fixed and growing \(\delta=e-d\):
\[
a^5+b^5+c^5=(d+\delta)^5-d^5.
\]
- Find congruence restrictions on \(\delta\).
- Prove nontrivial bounds on \(a,b,c\) for \(\delta=o(d)\).
- Search for a rigorously justified family, or prove finiteness in special regimes.

**Deliverable:** unconditional lemmas before formulating strengthened conjectures.

## P4 — Counting and asymptotics

- Derive unconditional height bounds, taking care with accumulated contributions from special rational subvarieties.
- State exact heights, ordering, and primitive conventions.
- Evaluate (but do not assume) logarithmic growth and shape equidistribution.
- Publish negative results and disproved conjectures with explicit counterexamples.

## Evidence labels

Use **PROVED**, **COMPUTATIONALLY VERIFIED** (with bounded domain), **HEURISTIC**, **CONJECTURAL**, or **REFUTED**. A CI pass certifies software invariants, not open number-theoretic statements.

## P0 — Braun 2026 source audit (2026-10-25)

The repository now records Braun's exact signed primitive tuple with an
independent integer/GCD/sign verification, and pins the author-reported
nonnegative `e≤2,760,000` and signed `e≤1,450,000` exhaustive coverage
limits separately from their **partial** larger ranges. These third-party
coverage claims have **not** been reproduced here. See the
[versioned primary-source audit](literature/2026-10-25-braun-v4-source-audit.md)
and [machine-readable evidence ledger](../data/literature/braun_2603_05549_v4.json).

**Next P1 gate:** implement a bounded unordered pair-sum residue partitioner
(Mojo-first, Python independent oracle); prove preservation of all candidate
pairs, no overlap between partitions, and no confusion between the
nonnegative and signed/zero-term regimes. Only then compare its measured
performance against the existing sorted membership search on identical
explicitly bounded domains.

## Pair-sum residue partition milestone

The small positive-domain partition prototype, source-level Lean coverage and
multiplicity proofs, independent Python conformance checks and deterministic
manifest are described in [the partition contract](PAIR_PARTITION.md).

## P2 bounded bucket traversal and independent replay

The [one-pass traversal contract](BUCKET_TRAVERSAL.md) implements a
representation-preserving residue lookup and domain-separated per-key replay
for the same strictly positive B<=144 domain. It is finite execution evidence,
not a large-range census, runtime speedup assertion, or a conjecture proof.

## P0 shared exact-arithmetic integration

The [exact arithmetic bridge](EXACT_ARITHMETIC_BRIDGE.md) gives the
bounded native census and packed-index search checked integer operations
and shares BigZ and gcd with the signed known-solution verifier. This
is a prerequisite for evaluating larger bounds, not permission to widen
those bounds or to promote finite computation into a theorem.

## P12 BigZ sorted-permutation proof and compiled sorting conformance

[The exact BigZ mergesort proof](BIGZ_MERGESORT_PROOF.md) establishes
transitive/total structured comparator, sortedness, multiplicity-preserving
permutation and nondecreasing sum projection, discharging the formal
P11 lower-bound sortedness hypothesis. The actual production Mojo
mergesort is independently checked against Python on signed/multi-limb
and colliding records; compiler-level universal refinement remains open.

## P11 BigZ exact ordering and Lean lower-bound trace refinement

The [BigZ signed lower-bound proof and trace contract](BIGZ_LOWER_BOUND_REFINEMENT.md)
uses the same native BigZ production comparison path in traced and untraced
execution; Python and Lean independently replay bounded >Int64 observation
transcripts against the kernel-checked arbitrary signed lower-bound theorem.
The B320 native result and pinned digest are unchanged.

## P10 complete 2..320 exact native BigZ plan and historical root reconciliation

The [dedicated full B320 BigZ workflow](BIGZ_B320_COMPLETE.md) executes
all 80 width-four target-height shards, independently checks every
actual native PART/CERT output and replays historical B144 and B256
prefixes against archived roots. This is a bounded computational
achievement only after the hosted workflow passes and preserves its
accepted actual transcripts; no extrapolation to unbounded solutions.

## P9 independently accepted full B144 BigZ search

The [B144 native BigZ crosscheck](BIGZ_B144_CROSSCHECK.md) runs all
36 consecutive 4-height shards and independently checks each native
transcript before comparing its reconstructed canonical PART/CERT rows
against the historical B144 fixture and SHA roots. This strengthens
cross-algorithm bounded evidence without claiming B256/B320 whole
range execution or a universal theorem about compiled completeness.

## P8 BigZ gap-free height coverage and independently replayed receipts

The [BigZ shard plan and receipt contract](BIGZ_PLAN_RECEIPTS.md)
provides deterministic 2..B plans, explicitly bounded native Mojo
worker execution, scoped retry/abort records and independent exact
Python replay before publication of a finite accepted manifest.
The CI acceptance corpus covers every height 2..12, not 2..320.

## P7 structured BigZ pair indexing and bounded E5 shards

The [Mojo native BigZ shard contract](BIGZ_SHARDS.md) introduces a lossless
ordered BigZ record `(sum,a,b)`, stable mergesort, binary lower-bound,
exact positive fifth-power complements, and explicit short height ranges
validated against an independent Python oracle. No new complete extended
range or production-scale result is claimed; complete shard coverage and
replay receipts are the next obligations.

## P6 B256 exact checked indexing

[The wide radix 257 proof and finite replay contract](B256_WIDE_INDEX.md)
extends the positive packed-index bound from B144 to B256, retains
historical B144 output, and independently checks all B256 canonical
partition rows and certificates. Larger or arbitrary-precision
searches still require a separately implemented typed pair index.

## P5 composite modulus selection and stronger three-digit CRT filters

See [the 99000 modulus-selection contract](MODULUS_SELECTION.md). It
combines mod 9 digit sums, mod 11 alternating sums, and last-three-digit
mod 1000 information. Its independently verified B144 prefix
eliminates 465,238 of 475,063 positive-complement right-pair visits
while preserving canonical partition and witness records. Actual
runtime is separately benchmarked against the P4 filter; the larger
residue table consumes more memory and may not outperform it.

## P4 decimal digit sums and CRT prefix filtering

The [exact digit/CRT pruning contract](DIGIT_SUM_PRUNING.md) promotes
generic decimal folds and a complete pair-power residue prefix to the
pinned `finite-math-kernels` library. Euler search uses modulus 2475
as a sound prefilter before exact index lookup, keeping partition
counts and certificates unchanged. The independently verified B144
counts reject 356,770 of 475,063 positive-complement right pairs;
native same-host timing is tracked separately and does not follow
from a rejection percentage alone.

## P3 packed representation index

The [indexed representation-search contract](PACKED_PAIR_INDEX.md) stores
all (sum,a,b) pair records in a bounded fixed-radix Int64 multiset,
replaces per-hit quadratic reconstruction with exact-sum range lookup,
and compares P2 vs P3 using the pinned native toolchain. It adds Lean
encoding lemmas and independent synthetic collision checks. Keep runtime
measurements and search-completeness claims separate from theorems.
