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

[P20](SIGNED_TWO_GAP_SEARCH.md) subsequently executed a first signed two-gap
experiment with u>b. Its finite negative result and measured resource use
are now logged separately. Future work must explore undeclared territory
or new constructions; the genuinely new primitive goal remains unmet.

## Candidate admission from any method

Every method must feed the same admission process: accept exact rational
or integer five-term zero-sum proposals with method/provenance, clear
nonzero denominators, compute the primitive signature and compare known
classes. Independently verify both cleared input and normalized primitive
residuals/gcds with native BigZ and Python arithmetic. A known class remains
known; an unknown class requires current literature review. Caller-supplied
classification and discovery labels carry no authority.

The generic intake is implemented in `tools/primitive_candidates.py` and
`discovery/verify_candidate.mojo`. Run `pixi run --locked verify` to initialize
the pinned dependency, then `pixi run --locked python tools/primitive_candidates.py
proposal.json --output fresh-result-directory`. It stores original input,
native stdout and source/run-bound receipt; it never announces a discovery.

The [accepted hosted conformance receipt](../data/algebra/candidate-intake-40408676983-accepted.json)
preserves the original archive and decoded job log. All 20 known-class exact
rational/scaled proposals, 42 native arithmetic invocations, six malformed
refusals and 1,440 Python equivalence cases pass. Independent local Python
replay checks every stored result. This is conformance only, with zero search
coverage. The hosted job used 3.59 seconds wall time and 247,600 KiB maximum
RSS including compilation and Python; these are not search throughput metrics.
A later [clean-dependency conformance run](../data/algebra/candidate-intake-40421223476-accepted.json)
also passed after adding wrong-HEAD and tracked/staged/untracked checkout
refusal controls: 3.53 seconds wall and 249,712 KiB peak RSS. Both original
archives remain preserved as zero-coverage conformance evidence.

Example proposal (a known calibration identity, not a discovery):

```json
{
  "schema": "E5-CANDIDATE-PROPOSAL-v1",
  "terms": ["27/7", "84/7", "110/7", "133/7", "-144/7"],
  "method": "exact rational construction",
  "provenance": "Lander-Parkin calibration; testing normalization only"
}
```

Implementation proposals must preserve original inputs, actual native stdout,
source/run hashes and immutable receipts. Finite intake digit caps and search
bounds are resource policies rather than restrictions on the mathematical
goal. Every denominator must be checked nonzero before exact division; no
floating-point base is accepted as an exact candidate.

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
