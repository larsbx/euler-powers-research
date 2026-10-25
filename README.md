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
- [Lean and Quint formal verification contract](docs/FORMAL_VERIFICATION.md)\n- [Independent Python reference](tests/verify_known_solutions.py)

Run the exact arithmetic checks with:

~~~sh
python3 tests/verify_known_solutions.py
~~~

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
manifest are described in [the partition contract](docs/PAIR_PARTITION.md).
