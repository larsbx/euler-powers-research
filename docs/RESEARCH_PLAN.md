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
