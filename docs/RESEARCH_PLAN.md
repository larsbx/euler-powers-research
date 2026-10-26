# Proof obligations and research stages

**Primary objective revised:** [a genuinely new primitive fifth-power class, positive or signed](DISCOVERY_OBJECTIVE.md), using any justified finite method. The next strategy obligation is a general signed region outside abs(a)<=b or a new exact algebraic construction; single-height grid expansion must be justified by discovery value. The [machine-readable charter](../data/DISCOVERY_CHARTER.json) and [candidate intake](DISCOVERY_OBJECTIVE.md#candidate-admission-from-any-method) specify exact normalization, independent native/Python arithmetic, equivalence de-duplication and mandatory current literature review. Native hosted conformance and independent Python replay pass; this is admission infrastructure with zero new search coverage. No discovery is claimed by this revision.

**P19 accepted computational result:** [larger minimum summands and residue-first evaluation](POST_BRAUN_P19.md): 724,549,632 new exact trials, 1,620,700 BigZ lookups and zero primitive identities. Six positive gaps and supported signed delta=4 extend abs(a) to 4096 at e=2,760,001. Cumulative unique high-height work is 2,441,336,576 trials in 63 cells. The before/after benchmark checks identical production stripes and reports sample-specific measured time reductions; no universal or whole-search ratio is inferred.

**P18 accepted:** [sixteen untouched positive gaps 17..32](POST_BRAUN_P18.md), 786,334,720 new exact trials, 1,340,424 BigZ lookups and zero primitive identities. The [current map](../data/experiments/TERRITORY.md) records 56 disjoint high-height cells and 1,716,786,944 trials. Positive e=2,760,001, delta=1..32, a<=1024 is complete only as this restricted block. [Pair reconstruction](PAIR_SUM_RECONSTRUCTION.md) is a separate exact algebra experiment; cached-production benchmarking remains open.

**P17 accepted:** [ten previously untouched positive gaps](POST_BRAUN_P17.md), 409,884,672 new exact trials and zero primitive identities. The [cumulative map](../data/experiments/TERRITORY.md) records 930,452,224 disjoint high-height trials, full B320 coverage and separate test-covered domains; e=2,760,001 positive delta=1..16, a<=1024 is now complete as a restricted block.

**P16 accepted:** [new a=257..1024 cells and exact two-term c bounds](POST_BRAUN_P16.md): 318,981,888 trials; 965,191 lookups; zero primitive identities. Positive coverage now reaches a=1024 at eight declared gaps, with a separate restricted signed mode; no full-height claim.

**P15 accepted:** [11 disjoint positive/signed frontier cells](POST_BRAUN_FRONTIER.md): 176,372,608 exact trials; 524,286 lookups; zero primitive identities. Complete only within the stated cells and magnitude ordering. Raw accepted evidence is permanent in data/experiments.
**Post-Braun P14:** [modular fifth-power image refinements and complete nine-cell fixed-(e,delta,a-cap) grid](POST_BRAUN_GRID_REFINEMENT.md) now runs rigorous c-interval coverage for e=2,760,001..2,760,003 and delta=1..3, a<=64. This is neither a complete target-height search nor a third known positive identity.

**Post-Braun P13:** [finite discovery-oriented high-height Mojo stripes](POST_BRAUN_DISCOVERY_STRIPES.md) search fixed (e,delta,A) slices with exact BigZ and independently replayed c-interval coverage. First target: e=2,760,001, delta=1, a<=64. This is a restricted slice even if every c is covered.

**Literature-first gate:** [Known primitive E5 source/novelty registry](KNOWN_PRIMITIVE_E5_LITERATURE.md) enumerates four nontrivial primitive source classes (two strictly positive) and disallows announcing permutations, scalar multiples or signed examples as novel positive discoveries.

**Primary goal:** [Discover a genuinely new primitive identity, positive or signed](DISCOVERY_OBJECTIVE.md). All four audited identity classes are calibration fixtures. Proofs, benchmarking, modular constraints, algebra and finite computation must serve discovery or independent validation; no finite census bound is the research endpoint.


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
