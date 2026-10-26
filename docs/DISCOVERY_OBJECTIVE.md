# Primary objective: a genuinely new primitive fifth-power identity

Find a new nontrivial primitive class of exact integer solutions to

```text
x1^5+x2^5+x3^5+x4^5+x5^5 = 0
all xi != 0
gcd(|x1|,|x2|,|x3|,|x4|,|x5|) = 1
```

Equivalently, present it as `a^5+b^5+c^5+d^5=e^5` with positive e and
signed nonzero summands. Strictly positive and signed identities both
satisfy the discovery goal; their sign classifications remain separate.
The primary target is no longer restricted to a third positive example,
one target height, small cancellation gaps, small first summands or the
current controller's `abs(a)<=b` ordering. Repeated largest magnitudes are
permitted unless they create literal opposite cancelling terms. Any scope
beyond the literature snapshot requires its own current novelty review.

The machine-readable [discovery charter](../data/DISCOVERY_CHARTER.json)
encodes this objective. A new primitive class, independently verified and
distinguished from the literature, is the success metric. Larger trial
counts, negative cells, faster kernels, proof counts and merged PRs are
supporting progress; none alone fulfills the discovery goal.

## What counts as the same identity

Represent every proposal by five signed terms whose fifth powers sum to
zero. Clear exact rational denominators, divide all five integers by their
positive gcd, sort, and choose the lexicographically smaller of that tuple
and its global negation. This canonical primitive signature identifies
permutations, movement of terms across the equality, global sign reversal
and common rational/integer scalings as the same class.

All five bases must be nonzero. Literal cancelling opposite terms are
excluded. Dividing out a common factor makes a presentation primitive but
does not create a new class. The four-entry audited snapshot includes
Lander-Parkin, Frye, Scher-Seidl and Braun; all remain calibration fixtures,
including signed rearrangements and arbitrary exact rescalings.

A candidate absent from that finite snapshot is not automatically new.
Before a discovery claim, perform current primary-source literature and
equivalence review, preserve the cited sources and report the precise sign
class. Signed results never increment the strictly positive result count.
The snapshot is not a theorem that these are all existing solutions.

## Methods and strategy

Use whichever justified finite method offers a credible route to a new
class: exact algebra, rational constructions, cyclotomic factorization,
pair-sum reconstruction, general signed cancellation, streamed or indexed
meet-in-the-middle searches, sound modular/prime-power sieves, and bounded
native computation. Heuristics may generate or prioritize proposals; exact
arithmetic and novelty checks determine acceptance. No method inherits
correctness or discovery status merely from being on this list.

The next strategy obligation is to explore a new structural direction:
general signed boxes with `abs(a)>b`, or an independently derived algebraic
construction. Select finite bounds from measured resource data and check
overlap against the accepted ledger before executing. Further refinement
of the single-height grid requires a discovery rationale, not just an
opportunity to increase the trial total. Strategies may be replaced when
measurements or mathematics show poor value.

The existing positive and supported signed controllers remain useful
tools. Their caps are experiment policies, not definitions of the goal.
Existing accepted cells and limitations remain unchanged; this objective
revision adds no search coverage or new identity.

## Candidate admission from any method

`tools/primitive_candidates.py` accepts five exact rational strings plus
method/provenance, clears denominators and computes the primitive signature.
It checks all five nonzero bases, excludes cancelling terms, verifies the
fifth-power residual and gcd, and compares against the registry snapshot.
It then invokes `discovery/verify_candidate.mojo` on both the cleared input
and normalized primitive tuple, checking the actual BigZ residual and gcd
against independent Python arithmetic. A known class remains known; an
unknown class remains a candidate requiring current literature review.
The tool never emits `discovery_claim=true`.

Example proposal (a known calibration identity, not a discovery):

```json
{
  "schema": "E5-CANDIDATE-PROPOSAL-v1",
  "terms": ["27/7", "84/7", "110/7", "133/7", "-144/7"],
  "method": "exact rational construction",
  "provenance": "Lander-Parkin calibration; testing normalization only"
}
```

```sh
pixi run --locked verify
pixi run --locked python tools/primitive_candidates.py proposal.json --output /tmp/candidate-new
```

Output directories are exclusive and contain the original proposal, actual
native stdout for cleared and primitive inputs, source/run hashes and a
receipt. Current intake policy permits up to 128 decimal digits per rational
component and 1024 per native integer base; these are finite resource limits,
not mathematical restrictions or a claim to cover larger inputs. Every
denominator is checked nonzero before exact division. No floating-point
value is admitted as a candidate base.

## Evidence and reporting

Every discovery experiment must declare finite work/time/memory and scope,
preserve raw source-bound evidence, and independently replay exact arithmetic.
Keep algebra tests, calibration, benchmarks, repeated runs and external
coverage reports separate from new search territory. A finite negative result
does not establish global nonexistence. Neither a literature lookup nor
native/Python agreement proves that an unsearched region is empty.

The stop condition is a genuinely new primitive identity with completed
arithmetic, equivalence, provenance and current novelty review. No new
identity is claimed by this charter revision or its conformance tests.
