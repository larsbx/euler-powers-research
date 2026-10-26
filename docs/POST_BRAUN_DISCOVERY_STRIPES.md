# P13 — Post-Braun discovery-oriented high-height stripes

The north-star remains a **third genuinely new strictly positive
primitive fifth-power solution**, not another formal theorem count.
The dated [published-primitive registry](KNOWN_PRIMITIVE_E5_LITERATURE.md)
has only two strictly positive examples. Braun (2026, arXiv
2603.05549v4) *reports* exhaustive nonnegative target-height coverage
through e<=2,760,000; **our repository has not reproduced that large
search**. A slice with e=2,760,001 is beyond that **author-reported**
threshold, but not a statement about all solutions at that height.

## Target and finite completeness semantics

For exact e, delta=e-d and first-base cap A, define

```text
D=e^5-(e-delta)^5=a^5+b^5+c^5,
1 <= a <= min(A,b) <= b <= c <= d < e.
```

The rigorous c interval is

```text
min_c = smallest c satisfying 3*c^5>=D
max_c = largest c<=d satisfying c^5<=D.
```

These are computed with integer BigZ fifth powers, binary comparisons
and NO approximated roots. The compiled Mojo
`kernel/near_cancellation_stripe.mojo` searches every
`(a,c)` combination for a declared closed c interval within these
bounds. Each candidate b is located with exact cached BigZ b^5
binary search after a **necessary-only**, complete b^5 residue-set
membership test in Z/99000Z; final quintuple equality and gcd are
checked again.

The higher-height input intake is explicitly bounded:
e<=4,000,000, 1<=delta<=256, 1<=A<=64,
`c_end<=600,000`, and no more than 4,096 c values per worker.
These are resource policies, not Diophantine facts.

The separate Python controller `tools/search_novel_stripes.py`
constructs a deterministic gap-free partition of **every**
mathematically admissible c for exactly (e,delta,A), runs the actual
compiled Mojo worker for each stripe, and independently regenerates
every output line, modular rejection count, exact lookup count and
witness using a **different algorithm**: Python arbitrary integer
hash-indexed b^5 lookup, NOT the native binary search. Any
failure, missing range, count mismatch or unexpected output prevents
publication of an accepted record.

All transcripts, source SHA-256 values, finite scope, SHA-256 hashes,
and admitted witnesses are recorded as
`E5-DELTA-STRIPE-ACCEPTANCE-v1`. A recorded witness is classified
as a *literature-review candidate* unless it matches the dated known
registry; a nonmatching result is not automatically new.

## First genuinely post-reported-coverage computation

Dedicated hosted CI `.github/workflows/discovery-stripe.yml`
executes the entire fixed slice:

```text
e=2,760,001
delta=1, so d=2,760,000
a in [1,64]
c in the ENTIRE exact algebraically admissible interval
b solved exactly; 1<=a<=b<=c<=d.
```

This is a meaningful new **parameter slice**, not a complete search
through e=2,760,001. The runner retains the actual native transcript
for each stripe, independent exact Python verification and GNU time
resource profile. **Before CI passes, no nonexistence claim is made.**
On success, a zero-witness result excludes solutions only with this
specific e, delta and a-cap, not other deltas or larger a.

The existing native search and independent Python reference still
rediscover the Frye witness at `e=85359,delta=77,a<=64`, and
the new stripe test includes c near 28969 as a regression.
The historical B320 full-height census and its pinned root remain
mandatory independent CI.

## Scaling research priorities

1. Use observed wall/RSS cost and rejection rate for a large e,
   rather than extrapolating the tiny B144 97.93% filter rate.
2. Expand finite `(e,delta,A)` stripes only when their exact
   resource budget is measured, especially additional delta classes
   and values of A which do not impose unrealistic small-a priors.
3. Develop direct parametric identities / number-theoretic
   obstructions that permit exploration of a much larger proportion
   of candidate space than sparse small-a stripes.
4. Upgrade toward reusable/streamed power tables, safe multi-host
   scheduling and source-bound acceptance receipts without claiming
   machine hashes are cryptographically signed worker attestations.

The result of this milestone, even with a fully passing zero-hit
post-Braun stripe, would be **negative finite evidence**, not a
third primitive positive solution. Discovery remains open.
