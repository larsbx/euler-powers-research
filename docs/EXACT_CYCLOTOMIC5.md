# Exact fifth-root-of-unity algebra

This branch develops exact algebra for the existing integer fifth-power
objective. It introduces no new solution, search cell, or rejection rule.
Complex approximations and analytic operations are unnecessary: work in
the ring `Z[X]/(Phi_5(X))`, where `Phi_5(X)=1+X+X^2+X^3+X^4`.
Write `z` for the residue class of `X`. Every element has the unique form
`a0+a1*z+a2*z^2+a3*z^3`, with integer coefficients.

## Implemented arithmetic

`algebra/cyclotomic5.mojo` supplies addition, subtraction, multiplication,
the four substitutions `z -> z^k` for `k=1..4`, and the product of those
four conjugates (the norm). All coefficients and intermediate products use
the same SHA-pinned native BigZ dependency as the search. Inputs outside
the four-coefficient representation or the Galois exponent range raise.
There is no division, floating point, root extraction, or numerical tolerance.

Multiplication first folds exponents modulo five (`z^5=1`), then eliminates
`z^4=-(1+z+z^2+z^3)`. The independent Python oracle instead performs monic
polynomial long division. Its norm is a 4-by-4 multiplication-matrix
determinant evaluated as 24 signed integer products, rather than a product
of conjugates. A non-scalar native conjugate product raises an error.

## Exact identities and necessary conditions

Put `Q(x,y)=x^4+x^3*y+x^2*y^2+x*y^3+y^4`. Then

```text
N(x-y*z) = Q(x,y)
x^5-y^5 = (x-y)*Q(x,y)
x^5+y^5 = (x+y)*Q(x,-y)
Q(y,y) = 5*y^4
Q(x,y) = (x-y)*(x^3+2*x^2*y+3*x*y^2+4*y^3)+5*y^4
Q(y+t,y) = t^4+5*y*t^3+10*y^2*t^2+10*y^3*t+5*y^4
Q(y+5*k,y) = 25*(25*k^4+25*y*k^3+10*y^2*k^2+2*y^3*k)+5*y^4
```

The last identity implies `Q(y+5*k,y) == 5*y^4 (mod 25)`.
If `5` does not divide `y`, its fourth power is `1 (mod 5)`, so the norm
is `5 (mod 25)`: it has exactly one factor of five. Also, every common
divisor of `x-y` and `Q(x,y)` divides `5*y^4`, directly from the displayed
remainder identity. These statements allow signed integers and the zero
cases; the exactly-one-factor conclusion requires the stated nondivisibility.

`formal/lean/Cyclotomic5.lean` proves twelve theorems: eight universally quantified integer
polynomial/remainder statements, including both fifth-power factorizations
and the modulo-25 equality; associativity, commutativity and the unit law
for an explicit integer coefficient model of multiplication; and the scalar
norm formula as a product of the four explicitly represented conjugates.
The existing axiom audit imports them. The formal file does **not** yet
construct an abstract quotient ring or a general norm/automorphism API,
prove the determinant equivalence, or verify the native arithmetic
implementation and compiler lowering. Those implementation comparisons
have independent computational conformance checks.
The fourth-power unit observation and common-divisor corollary above are
elementary consequences, not separately named Lean theorems here.

## Consequences for search

For fixed `(e,d)`, the norm factorization is an identity for every input.
It cannot distinguish the remaining `(a,c)` trials on its own. The
modulo-25 condition also does not supply a new independent scalar residue
modulus beyond the existing modulo-99000 gate (`25` divides `99000`).
This is not a claim that every possible factor-based algorithm is redundant.
No speedup, new rejection count, or additional searched territory is claimed.

A useful next obligation is to derive a restriction on the unknown
summands from a factorization of a remaining pair sum, with all gcd and
coprimality cases explicit. It must then be compared with the existing
bounded fifth-power images and measured before becoming a search filter.
Primitivity of all five entries does not imply pairwise coprimality; that
assumption must never be silently added. No unique-factorization or prime
splitting theorem is assumed by this implementation.

## Reproduction and evidence classes

```sh
python tests/test_cyclotomic5.py --python-only
pixi run --locked python tests/test_cyclotomic5.py --output /tmp/cyclotomic5-new
pixi run --locked python tests/test_cyclotomic5.py --verify --output /tmp/cyclotomic5-new
cd formal/lean
lake build Cyclotomic5
lake env lean Audit.lean
```

The native transcript covers all 81 elements with coefficients in
`{-1,0,1}` and all 6,561 ordered pairs for each of addition, subtraction,
and multiplication; all four automorphisms and 81 norms; 16 repeated large
multiplications and norms; eight signed/zero/known-height scalar norm pairs;
and four invalid-input controls. It has exactly 20,139 lines. The large
cases exceed Int64 by many orders of magnitude. Python additionally checks
basis associativity, automorphism composition and multiplicativity, and
the signed scalar identities on all 22,801 pairs in `[-75,75]^2`.

The dedicated hosted workflow records source-file SHA-256 hashes, the
pinned dependency SHA, GitHub source/run labels, raw native bytes and their
hash, GNU time wall/user/system/maximum RSS, and independent replay timings.
`--verify` rebuilds the entire expected transcript and checks the source,
scope, raw bytes, receipt and resource hashes without replacing measurements.
The receipt is a reproducibility record, not a signed remote attestation.
The all-repository Lean/Quint workflow checks the new proofs separately.

This is **algebra conformance evidence**, not search coverage. The accepted
territory ledger and its trial count remain unchanged.

## Accepted native execution

[Hosted run 40350072406](https://github.com/larsbx/euler-powers-research/actions/runs/40350072406)
passed native conformance and the fresh full independent replay, at source
head `bc53176dc262674c8a83bf4b46cb58a29ce98eaa`. The receipt's `GITHUB_SHA`
is the synthetic PR test merge `adeae7e10bf7aca056ab0802bcbccf6c88975a3d`.
The raw artifact (ID `12663447063`, five files) is preserved permanently as
[cyclotomic5-40350072406.zip](../data/algebra/cyclotomic5-40350072406.zip),
with [an inspectable receipt](../data/algebra/cyclotomic5-40350072406-accepted.json).
Its SHA-256 is
`e04d757ddcaae40eb8300d3c85dc4e78f888b713feec079f87ec8b777b34071a`.
The transcript hash is
`dd8aa82405162b8d4bd6cf2d0f057698e9045d50911afb4ba8869994f564c179`.

| Measured process | Wall seconds | User seconds | System seconds | Maximum RSS KiB |
| --- | ---: | ---: | ---: | ---: |
| Native invocation, including wrapper/compiler/execution | 4.46 | 5.02 | 0.27 | 257,036 |
| Full acceptance process, including Python checks and native invocation | 4.85 | 5.39 | 0.33 | 257,036 |
| Separate fresh Python replay process | 0.23 | 0.20 | 0.02 | 69,284 |

These are conformance-process measurements, not a search benchmark or a
measurement of a precompiled kernel alone. The 16 large cases reach
145-digit coefficients and a 577-digit norm. After artifact download, ZIP
SHA-256, CRC, file/source hashes and the complete transcript were checked
again by a separate local Python replay. The first native attempt, run
`40349854407`, failed at compilation because of probe list-construction
syntax; it produced no accepted receipt. The corrected run above passed.

To replay the preserved evidence, extract the ZIP into a fresh directory
and run `python tests/test_cyclotomic5.py --verify --output EXTRACTED/cyclotomic5`
using the source files with the receipt's recorded hashes. Later commits
may add proofs or documentation without changing those arithmetic sources.

The next exact algebra experiment is now accepted: [signed pair reconstruction](PAIR_SUM_RECONSTRUCTION.md), with divisor/square reconstruction proofs, native comparison and preserved mixed timing results. It adds no Euler search coverage.
