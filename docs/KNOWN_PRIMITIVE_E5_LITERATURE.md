# Literature census: known nontrivial primitive fifth-power identities

**Literature review date: 2026-10-26.**

The fixed research equation is

```
a^5 + b^5 + c^5 + d^5 = e^5
```

with integer **nonzero** summands, `e>0`, all other bases
smaller in absolute value than `e`, and five-way gcd equal to 1.
A strictly positive solution further requires `a,b,c,d>0`
and orders them `1<=a<=b<=c<=d<e`.
We count solutions up to permutation, moving terms between the two
sides (with sign changes), and reduction by common positive factors.
Zero-term cancellation families and equations with other numbers
of summands are deliberately **outside this nontrivial corpus**.

## Four documented primitive equivalence classes

| Date | Source attribution | Canonical `(a,b,c,d;e)` | Target `e` | All four positive? |
| --- | --- | --- | ---: | --- |
| 1966 | Lander–Parkin | `(27,84,110,133;144)` | 144 | **Yes** |
| 1996 | Scher–Seidl | `(-220,5027,6237,14068;14132)` | 14,132 | **No** |
| 2004 | Jim Frye | `(55,3183,28969,85282;85359)` | 85,359 | **Yes** |
| 2026 | Jeffrey M. Braun | `(-1340632,719115,1331622,1956213;1956878)` | 1,956,878 | **No** |

All four are **independently verified exact fifth-power identities
with gcd=1**. The sum on the left is checked with arbitrary-precision
Python integers and separately by the existing Mojo verifier. The
normalized signs above place the smallest signed base first.
A positive integer multiple cannot be primitive because its
five-way gcd is the multiplier; a permutation or equivalent
rearrangement is not a new underlying five-term zero-sum identity.

Both signed examples can instead be written as balanced
**two-fifth-powers versus three-fifth-powers**:

```text
14132^5 + 220^5
    = 14068^5 + 6237^5 + 5027^5

1956878^5 + 1340632^5
    = 1956213^5 + 1331622^5 + 719115^5
```

They are important primitive identities in the **integer** problem,
but do **not** provide new strictly positive four-summand identities.

### Primary and contemporaneous provenance

- **1966, original published result**: L. J. Lander and
  T. R. Parkin, *Counterexample to Euler's conjecture on sums of
  like powers*, *Bulletin of the AMS* 72 (1966), p.1079.
  https://doi.org/10.1090/S0002-9904-1966-11654-3
- **1996, contemporary research announcement**:
  Bob Scher and Ed Seidl, *Massively Parallel Number Theory*,
  Sandia result announcement, archived June 1997.
  https://web.archive.org/web/19970608041930/http://midway.ca.sandia.gov/~mecolv/euler/
  The document gives `14132^5 + 220^5 -
  14068^5 - 6237^5 - 5027^5=0`. The 1996 attribution
  is followed by Braun's 2026 references; archival date is 1997.
- **2004, unpublished mathematical discovery and contemporary report**:
  Jim Frye, reported by Ivars Peterson in *Science News*,
  *Euler's Sums of Powers*, September 24, 2004.
  https://www.sciencenews.org/article/eulers-sums-powers
  Corroborated by OEIS https://oeis.org/A134341 and Braun 2026.
  Frye's discovery is reported, rather than independently
  published as a mathematics paper.
- **2026, primary preprint**:
  Jeffrey M. Braun, *The fourth known primitive solution to
  a^5+b^5+c^5+d^5=e^5*, arXiv:2603.05549v4,
  revised August 21, 2026.
  https://arxiv.org/html/2603.05549v4
  Table 1 explicitly lists the earlier three and Section 3
  gives the fourth. The signed/positive distinction is explicit.

Additional contemporary corroboration:
Wolfram MathWorld https://mathworld.wolfram.com/DiophantineEquation5thPowers.html
and OEIS A134341 for strictly positive solutions.
The public fifth-power target index at
https://powersums.jorisperrenet.com/5th-powers/5-5-n/
also includes these four at target zero, but its many equations
equal to 1, 2, etc. are **not** solutions of the present equation.

### Computational evidence versus global exhaustiveness

Braun reports exhaustive **nonnegative** search coverage through
`e<=2,760,000`, and exhaustive **signed** coverage through
`e<=1,450,000`, with larger partially explored intervals.
See Section 6 of the cited v4 paper. These are **author-reported**
computations, **not** independently reproduced by our repository.
Do not extend the ranges, combine nonnegative and signed domains,
or treat either as an unbounded theorem.

Our own separately accepted native BigZ search covers the
strictly positive ordered primitive domain through `e<=320`,
and the discovery-oriented kernel independently rediscovers both
positive examples at their individual `(e,delta,a)` slices.
Those local validations **do not** prove the published literature
has no other large or unpublished primitive example.

**Conclusion at review date**: Four publicly documented
nontrivial primitive equivalence classes were identified:
**two** strictly positive and **two** with a negative term.
This is a curated, source-backed state-of-literature claim,
**not a mathematical proof that only four exist**.

## Machine-readable registry and novelty filtering

The audited metadata is in
`data/literature/known_primitive_e5_2026-10-26.json`.
The test `tests/test_known_primitive_registry.py` independently
crosschecks the four integer equations, gcd, sign domain, original
CSV, source identifiers, 5/11 residue guards and equivalence classes
under permutation, positive scaling and sign reversal of the
five-term zero-sum identity.

**Candidate policy:** A matching normalized class is **known**.
A new normalized class is only `not_in_curated_registry`
until separately verified against current mathematical literature
and independently checked numerically. Never automatically call
it a new discovery.

For finding a **third positive** result, searches below Braun's
author-reported nonnegative bound primarily serve as regression,
algorithm validation or independent replication; the best novelty
targets lie beyond those ranges or in exact algebraic constructions
with explicit source comparison.
