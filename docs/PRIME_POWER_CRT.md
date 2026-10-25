# P1 — Prime-power fifth-power rings and CRT verification

## Scope and actual source of computation

The primary executable is `kernel/prime_power_sieve.mojo`.
It calls the pinned `finite-math-kernels`
`finite_polynomial.polynomial_fp.Modulus` API, which implements exact
canonical arithmetic in **Z/mZ**, including composite moduli.
It **does not** mistake prime powers `p^k` for the prime field `Fp[p]`.

The suite accepts only a bounded, reviewed table of moduli and computes
complete finite profiles (not a search for integer solutions):

| Modulus | Prime | Distinct fifth powers | Exact zero-count mask |
|---:|---:|---:|---:|
| 5 | 5 | 5 | 47 |
| 25 | 5 | 5 | 42 |
| 125 | 5 | 21 | 42 |
| 625 | 5 | 101 | 42 |
| 11 | 11 | 3 | 42 |
| 121 | 11 | 23 | 42 |
| 31 | 31 | 7 | 47 |
| 61 | 61 | 13 | 47 |

The mask's bit `z` (0–5) denotes that some five-base residue tuple
satisfies `a^5+b^5+c^5+d^5-e^5=0 mod m` with **exactly z
bases divisible by the stated prime**. Mask 42 has bits 1, 3, 5.
Mask 47 has bits 0, 1, 2, 3, 5. The five-divisible case is
nonprimitive, but *other* choices satisfying a finite modulus condition
need not lift to integer solutions. In particular the table makes
no claim that 31 or 61 imposes a universal 1-or-3 law.

Each profile traverses **all** base residues mod m, constructs the
complete fifth-power image and a Boolean five-position modular DP.
The DP stores separate choices `(fifth_power_residue, divisible_by_p)`
so repeated fifth powers do not lose their divisibility labels.
The summand signs are `(+,+,+,+,-)`. The native emitter returns
`POWER modulus prime image_cardinality labelled_choices mask`.
The independent Python implementation uses set-valued Cartesian-state
transitions, not the native Boolean array structure.

`profile(m,p)` rejects composite `p`, moduli not a power of `p`,
out-of-range `m>625`, and invalid input. The fixed production suite
runs `5,25,125,625,11,121,31,61`; lifting to larger prime powers
requires an explicit arithmetic/performance resource review.

## CRT law and its limitations

For coprime positive integers `m,n`, the Chinese remainder theorem
gives an isomorphism

`Z/(mn)Z ≅ Z/mZ × Z/nZ`.

It commutes with the fifth-power map. Therefore the **full** fifth-power
image mod `mn` corresponds bijectively to the Cartesian product of
the two component images, so

`|R5(mn)| = |R5(m)| |R5(n)|`.

The executable checks this concrete identity at `(25,11)`,
`(125,11)`, and `(25,31)` against **direct enumeration**
of the fifth powers mod their products. The independent Python oracle
also exhaustively checks that the per-integer residue-projection map
is bijective and carries the image to the Cartesian product.
All products are <=2500; noncoprime CRT inputs are refused.

**Do not infer random or statistical independence.** A short bounded
integer search has coupled base bounds `1<=a<=b<=c<=d<e`;
its finite-range residue combinations need not factor into independent
components. The CRT law describes the *full* unrestricted residue ring,
not distribution or admissible bounded positive integer tuples.
Similarly, the known primitive modulo-11 and modulo-25 one-or-three
divisibility laws remain separate theorems, not new consequences of
statistical heuristics.

## Formally verified prefilter

`formal/lean/PrimePowerSieve.lean` proves for **every** modulus
`m>0` that every fifth power is in the enumerated complete finite
residue image, and for any modulus `m` that a valid primitive positive
solution's fifth-power complement occurs in the complete ordered
left-pair residue image at height `e`. It proves the same necessary
condition for **both** selected moduli without any claim of
independence, and proves the original equation reduces exactly modulo
every `m` (including prime powers). These are universal mathematical
claims under Lean's definitions. The pinned native executable is
cross-checked only on the finite suite, **not** compiler verified.

The subsequent [digit-sum/CRT prefilter](DIGIT_SUM_PRUNING.md) **does**
insert a proved sound bounded-prefix membership test into the production
search. The statements below describe the historical P1 milestone.

This PR **does not insert a new pruning rule into the production
search**. A later PR can construct bounded-height precomputed
left-pair residue sets, reject impossible candidates before the
packed exact index lookup, and measure the realized pruning. Any new
pruning path must maintain the B=144 nonempty witness, exactly reproduce
the existing partition digest and compare its counts with an
independent oracle on identical bounded domains.

## Commands, evidence, and trust

```sh
pixi run --locked python tests/test_prime_power_sieve.py
pixi run --locked verify-research
bash tools/verify-formal.sh
```

The tests execute the pinned Mojo binary, compare every emitted field
with Python arbitrary-precision modular exponentiation and set DP,
and exercise CRT projection bijections. The formal gate builds the new
Lean module and runs the global axiom audit. Existing bounded positive
census, signed known-solution, packed-index and Quint workflows remain
unchanged. All arithmetic remains exact; no real-valued or complex
approximations participate.

**Evidence status:** prime-power tables and particular CRT product
checks are `COMPUTATIONALLY VERIFIED (bounded moduli)`; general
residue-filter soundness is `PROVED (Lean)`. Nothing here establishes
exhaustive million-height searches, an infinite family or any E5
conjecture.
