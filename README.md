# Euler Powers Research

A proof-first program investigating Euler's sum-of-powers conjecture, especially primitive integer solutions of

\[
a^5+b^5+c^5+d^5=e^5.
\]

The original conjecture is false. The open questions concern **infinitude, algebraic structure, and distribution** of primitive positive solutions, and whether analogous counterexamples exist in higher exponents.

## Scope and conventions

We count positive, primitive tuples satisfying \(0<a\le b\le c\le d<e\) and \(\gcd(a,b,c,d,e)=1\). This eliminates permutation and common-scaling duplicates. Put

\[
N_5(B)=\#\{(a,b,c,d,e):e\le B,\ \text{with the preceding conditions}\}.
\]

Two positive primitive examples currently reported in the literature are

- \(27^5+84^5+110^5+133^5=144^5\) (Lander–Parkin, 1966);
- \(55^5+3183^5+28969^5+85282^5=85359^5\) (Frye, 2004).

Four primitive integer solutions are currently reported when **negative summands** are allowed; only two have all four summands positive. This distinction is essential.

## Research artifacts

- [Foundations and proved elementary lemmas](docs/FOUNDATIONS.md)
- [Open questions and conjecture hierarchy](docs/CONJECTURES.md)
- [Proof obligations and research stages](docs/RESEARCH_PLAN.md)
- [Literature reviews and weekly review protocol](docs/literature/README.md)
- [Braun v4 primary-source verification](docs/literature/2026-10-25-braun-v4-source-audit.md)
- [Exact known-solution data](data/known_solutions.csv)
- [Mojo-native BigZ verifier and pinned toolchain](docs/MOJO.md)
- [Finite-ring and bounded census implementation](docs/BOUNDED_SEARCH.md)
- [Exact prime-power residue rings and CRT verification](docs/PRIME_POWER_CRT.md)
- [Lean and Quint formal verification contract](docs/FORMAL_VERIFICATION.md)\n- [Independent Python reference](tests/verify_known_solutions.py)

Run the exact arithmetic checks with:

~~~sh
python3 tests/verify_known_solutions.py
~~~

### Shared exact-arithmetic bridge

The [P0 exact-arithmetic integration](docs/EXACT_ARITHMETIC_BRIDGE.md)
reuses pinned `finite-math-kernels` checked machine arithmetic, BigZ and
GCD across the positive census, packed pair index and signed known-solution
checker. Integer overflow raises rather than wrapping; no search bounds
or theorem status are changed.

## Research discipline

- Mark every claim as **PROVED**, **COMPUTATIONALLY VERIFIED** (with explicit range and code), **HEURISTIC**, or **OPEN**.
- Never infer infinitely many primitive solutions from rescaling; scaling preserves the identity but usually destroys primitivity.
- Keep positive-only and signed solutions separate.
- A lack of observed solutions is not a finiteness theorem.
- Finite-ring computations certify only the modulus actually checked.
- Any broad literature-completeness claim should carry a date and source.

## Sources

- Lander & Parkin, *Counterexample to Euler's conjecture on sums of like powers*, Bull. AMS 72 (1966), 1079.
- Jeffrey M. Braun, *The fourth known primitive solution to* \(a^5+b^5+c^5+d^5=e^5\), arXiv:2603.05549 (2026): https://arxiv.org/abs/2603.05549
- MathWorld, *Euler's Sum of Powers Conjecture*: https://mathworld.wolfram.com/EulersSumofPowersConjecture.html

## Formal verification

Lean 4 kernel-checks the arithmetic certificate predicate, the exact
complement identity underlying meet-in-the-middle enumeration, the shard
coverage and disjointness theorems, and canonical examples. Quint models
the shard submission, rejection and publication workflow with bounded
Apalache safety checks. These layers are not a proof of the conjectures
or a complete formal verification of the Mojo implementation.

```sh
bash tools/formal-setup.sh
bash tools/verify-formal.sh
```

CI requires the Lean/Quint gate alongside Mojo and its independent Python
oracle. See [the proof boundary](docs/FORMAL_VERIFICATION.md).

The Lean certificate replay executable checks live Mojo output and refuses
invalid reported solutions. This is not a proof of census completeness.

A Lean-executable contiguous height-shard validator now checks each actual
Mojo shard's reported witnesses and rejects gaps or overlaps in the declared
coverage plan. This is distinct from proving that each worker found every
solution. See [formal verification](docs/FORMAL_VERIFICATION.md).

The Mojo lookup now emits optional deterministic loop traces that an
independent Lean executable replays step-by-step in CI. This is finite
execution correspondence evidence, not a compiler-level proof of all runs.

## Pair-sum residue partition milestone

The small positive-domain partition prototype, source-level Lean coverage and
multiplicity proofs, independent Python conformance checks and deterministic
manifest are described in [the partition contract](docs/PAIR_PARTITION.md). The
[one-pass bucket traversal and independent per-key replay](docs/BUCKET_TRAVERSAL.md)
extend this bounded positive census without changing its arithmetic scope. The
[collision-preserving packed representation index](docs/PACKED_PAIR_INDEX.md)
replaces per-hit exhaustive reconstruction and records controlled native benchmarks.
**Verified literature baseline:** [four known nontrivial primitive fifth-power classes, only two strictly positive](docs/KNOWN_PRIMITIVE_E5_LITERATURE.md) — independently checked with exact integers, source citations and normalized permutation/scaling/sign equivalence.

**Systematic post-Braun search:** [independently replayed e-delta grid with exact mod-41/mod-61 fifth-power filters](docs/POST_BRAUN_GRID_REFINEMENT.md) extends the initial 2,760,001 single-slice trial to nine explicitly bounded parameter cells.

**Post-Braun exploration:** [independently replayed native Mojo high-height near-cancellation stripes](docs/POST_BRAUN_DISCOVERY_STRIPES.md) now target e=2,760,001 in a rigorously scoped delta=1, a<=64 trial beyond the author-reported nonnegative coverage, without calling an incomplete height search exhaustive.

**Research priority:** [Find the next, genuinely new primitive strictly positive fifth-power solution](docs/DISCOVERY_OBJECTIVE.md). Our two known positive reference identities are at e=144 and e=85359; scalable near-cancellation search, not merely more bounded formal proofs, is now the main discovery program.

The [BigZ exact merge-sort sorted-permutation theorem and native conformance](docs/BIGZ_MERGESORT_PROOF.md)
now closes the mathematical sorted-input precondition of the verified
signed lower bound and separately checks production Mojo sorting.
The [exact BigZ lower-bound trace and proof bridge](docs/BIGZ_LOWER_BOUND_REFINEMENT.md)
connects native arbitrary-precision pivot observations to Lean's signed
lower-bound theorem, with negative-control replay and no compiler proof claim.
The [full B320 BigZ height-census workflow](docs/BIGZ_B320_COMPLETE.md)
executes 80 consecutive Mojo BigZ shards and requires independent
replay plus historical B144/B256 prefix-root agreement before acceptance.
The [full B144 BigZ search crosscheck](docs/BIGZ_B144_CROSSCHECK.md)
executes every height 2..144 with the exact Mojo BigZ index and reconciles
independently replayed shard output against the earlier packed-index certificate.
The [gap-free BigZ height plans and independently replayed native receipts](docs/BIGZ_PLAN_RECEIPTS.md)
now distinguish a planned finite height range from verified execution of every shard.
The [Mojo-native structured BigZ pair index and bounded exact height shards](docs/BIGZ_SHARDS.md)
remove fixed-radix encoding for a separate independently validated shard runner.
The [B256 wide packed-index extension](docs/B256_WIDE_INDEX.md) now
checks larger positive candidate domains with fixed radix 257,
independent Python oracle replay and a new bounded SHA root.
The [99,000 CRT-modulus selection](docs/MODULUS_SELECTION.md) refines
three-digit, alternating-digit and digit-sum obstructions with independent
native timing and exact candidate retention tests.
The [exact decimal-digit/CRT prefix sieve](docs/DIGIT_SUM_PRUNING.md) now
uses a shared Mojo kernel to reject impossible complements before indexed
lookup, without changing canonical search records.

**Accepted discovery frontier:** [broader gaps, a=65..256, and separate one-negative-term cells](docs/POST_BRAUN_FRONTIER.md), 176,372,608 new exact trials, 524,286 lookups and zero witnesses; bounded native execution, independent full replay and durable raw evidence.
