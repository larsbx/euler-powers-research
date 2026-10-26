# Primary objective — discover a third primitive strictly positive fifth-power solution

## Research target

Find **a new, independently verifiable primitive positive tuple**

```text
1 <= a <= b <= c <= d < e
a^5 + b^5 + c^5 + d^5 = e^5
gcd(a,b,c,d,e) = 1
```

**Audited source baseline:** [Four known nontrivial primitive identities — two positive and two signed](KNOWN_PRIMITIVE_E5_LITERATURE.md). This is a public-literature census as of October 26, 2026, not a proof of global finiteness.

**Already known, and not discoveries:**

`(27,84,110,133,144)` — Lander–Parkin (1966).

`(55,3183,28969,85282,85359)` — Frye (2004).

The Scher–Seidl and Braun examples contain negative summands.
They must not be counted as primitive strictly positive solutions.
The certified complete B320 native BigZ census finds only the first
known positive tuple, as expected. **Extending B320 to B321 is not
a discovery milestone by itself.** The project should optimize for
finding a **third known-to-the-literature primitive positive example**,
or rigorously identifying a new positive parametric family.

The corpus verifies both known positive identities. Published
claims of searches extending to much larger bounds are relevant
external evidence but must not be presented as reproduced unless
the underlying search and coverage have independently been run.

## Discovery-first search: near cancellation

Set `delta = e-d` and use the exact algebraic identity

```
D(e,delta) = e^5 - (e-delta)^5
           = a^5 + b^5 + c^5.
```

Because `1<=a<=b<=c<=d`, we have

```
c^5 <= D <= 3*c^5
```

and therefore the **complete admissible** c range for one
`(e,delta)` slice is

```
ceil_fifth_root(D/3) <= c <= min(d, floor_fifth_root(D)).
```

`kernel/near_cancellation.mojo` computes these bounds with exact
shared BigZ multiplication/comparison; it uses **no floating roots**,
fractional exponentiation or external approximate numerical library.
It then scans all `a<=A`, all c in the rigorous interval, and
solves for b from the exact residual fifth power using binary search
over cached shared BigZ fifth powers. The modular image of b^5
in `Z/99000Z` is an inexpensive necessary prefilter; this never
authorizes or creates an integer witness. Final acceptance checks
the complete exact fifth-power identity and five-base GCD.

**Explicit scope**: The first implementation searches **one**
`(e,delta,A)` slice, with
`5<=e<=100000`, `1<=delta<=256`, `A<=128`, and
at most 10,000 admissible c values / 1,280,000 `(c,a)` tests.
It cannot claim absence of solutions at other target heights,
other deltas, or with `a>A`. The arbitrary-precision arithmetic
will remain correct even though the resource policy is finite.

## Non-negotiable calibration gates

The native Mojo engine must rediscover **both** known positive
solutions **without receiving their a,b,c coordinates**:

* e=144, delta=11, A=64 => (27,84,110,133,144).
* e=85359, delta=77, A=64 => (55,3183,28969,85282,85359).

The independent Python reference uses a hash map of full exact
b^5 values, not Mojo's sorted BigZ binary-search implementation.
It checks all emitted rows, mathematical bounds, residue rejects,
exact lookup counts, candidate identities and primitivity.
One exploratory forward slice `(e,delta,A)=(85360,77,64)`
is also tested with the same exhaustive *slice-specific* oracle.
A missing solution there is not a statement about any other e,
delta, or a value.

These milestones matter because the Frye target is far beyond
the prior B320 complete census; genuine algorithmic scaling has
to reproduce the second published target efficiently before
making conjectural third-solution discovery claims.

## P13: Search outside the author-reported nonnegative exhaustive height

The [post-Braun exact near-cancellation stripe protocol](POST_BRAUN_DISCOVERY_STRIPES.md) implements independently accepted complete c-stripes for an explicit e, delta and small-a cap, using native Mojo BigZ and an independent Python power hash oracle. The first target e=2,760,001, delta=1, a<=64 is beyond the *author-reported* nonnegative search height but remains a *restricted* parameter slice. Source provenance and negative-slice scope are mandatory.

## P14: Systematic novelty-region grid

The [post-Braun parameter grid](POST_BRAUN_GRID_REFINEMENT.md) adds exact mod-41 and mod-61 fifth-power image rejection before BigZ b lookup, then searches nine adjacent (e,delta) cells with complete finite c coverage. Every native line is reconstructed by a different Python exact-integer algorithm. The scope remains a<=64 and delta<=3, not a complete target-height census.

## Next experiments prioritized by discovery yield

1. Measure the native search's runtime and peak memory on the
   two known-solution slices. Benchmark the benefit of exact
   fifth-power residue prefiltering at large e; do **not**
   extrapolate the B144 97.93% rejection figure because residue
   tables saturate differently for larger base ranges.
2. Add deterministic `(e,delta)` stripe scheduling with strict
   finite `a` caps and complete coverage receipts, while
   preserving distinction between slice coverage and full height
   coverage. Use small initial forward exploratory stripes and
   report raw negative results.
3. Develop efficient two-stage modular obstruction tests that
   depend on the *bounded available b range*, using CRT,
   prime-power lifts with proven hypotheses, and near-cancellation
   restrictions. Profile candidate rejection per actual height.
4. Upgrade the kernel to a bounded external-memory/streamed
   meet-in-the-middle index for larger a and b, and sparse interval
   reuse between consecutive e and delta values. Avoid rebuilding
   O(e^2) pair maps for every height.
5. Investigate exact algebraic special loci/rational curves on
   the quintic threefold, requiring positivity and primitivity
   validation for each proposed family. Distinguish conjectural
   parameterizations from established exact identities.

**Acceptance criterion for a genuine discovery:** A third positive
tuple not already in the documented literature, exact Mojo BigZ
identity and GCD, independent Python replay, exclusion of scalar
duplicates, full search/source provenance and transparent external
literature comparison. A newly found height is not synonymous
with an exhaustive range theorem.

This is the research **north star**. Additional formal verification
and code abstraction are justified when they improve the chance of
discovering, validating or explaining a *new* primitive positive
fifth-power identity—not as ends in themselves.

## October 26 expanded discovery scope

The user also authorizes seeking a genuinely new signed primitive identity.
Relative to the four-entry literature registry this would be a fifth signed-or-positive
class, while the positive goal remains a third positive class. [P15](POST_BRAUN_FRONTIER.md)
adds a separately labelled one-negative-term search; it never counts signed
identities as positive discoveries.
