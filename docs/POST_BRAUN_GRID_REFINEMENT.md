# P14 — Modular fifth-power image refinement and post-Braun search grid

**Primary goal:** Discover a third genuinely new primitive strictly
positive solution of `a^5+b^5+c^5+d^5=e^5`.
Current source-backed baseline: Lander–Parkin and Frye (strictly
positive), Scher–Seidl and Braun (signed).

## Reduced expensive exact b-lookups, without losing candidates

The original high-height Mojo P13 filter tests whether each target
`b^5=D-c^5-a^5` belongs to the full set of fifth-power residues
modulo 99,000 attained by an admissible **positive b<=c**. That is a
necessary condition and cannot remove a true candidate.

P14 adds two more *independent*, complete finite-ring images:
`Z/41Z` and `Z/61Z`. Both primes have `5 | (p-1)`, so
their fifth-power images are proper subsets of all ring residues.
For each c, the engine incrementally records

```
R_m(c) = { b^5 (mod m) : 1 <= b <= c }
m in {99000,41,61}.
```

An exact candidate is rejected only if `target mod m` is absent
from **one of the complete bounded** `R_m(c)` tables. It then
uses the **same BigZ full integer binary lookup, primitive gcd and
equality checks** as P13, so solution sets must remain unchanged.
This is not a probabilistic independence claim; no Hensel lifting
or field-rational approximation is used. The independent Python
hash-indexed oracle separately constructs all three sets, counts
every rejected `(c,a)` pair and checks the full Mojo stdout.

The historical P13 run at `e=2,760,001,delta=1,a<=64`
covered all `157434<=c<=196119`: 2,475,904 candidates, 145,430
exact b-lookups and no primitive positive witnesses. These
historical numbers refer to the **old** modulo-99000 filter;
P14 introduces additional sound rejection gates, and its
hosted run must measure the new count rather than assuming any
fixed improvement.

## Systematic grid of newly targeted regions

`tools/search_discovery_grid.py` defines an explicit finite
Cartesian product of target heights and near-cancellation gaps.
Each cell has an independently verified complete c-covering
under the rigorous algebraic bound, and explicit `a<=A`.
It executes real native Mojo, invokes the independent Python exact
oracle through `tools/search_novel_stripes.py`, and checks every
child acceptance/record hash, c-interval and source identity
before publishing an aggregate *grid accepted* JSON. The
controller uses **exclusive fresh output directories**; a failed
rerun cannot mutate existing scientific evidence. It refuses
missing/duplicate/out-of-plan transcripts or parameter cells.

### Accepted native hosted nine-cell result

The first hosted grid execution **passed** with exact native Mojo
transcript replay by an independent Python power-hash oracle. It
executed every mathematically admissible c in all **nine** declared
cells (e=2,760,001..2,760,003; delta=1..3; a<=64):

- **25,213,056** (c,a) combinations tested.
- **56,409** exact b-fifth-power binary lookups after necessary
  modular and positivity filtering.
- **Zero** primitive strictly positive solutions in this
  restricted parameter grid.
- For the previously tested P13 fixed slice
  `e=2,760,001, delta=1, a<=64`, exact lookups fell from
  **145,430** with modulus-99000 alone to **3,519** using the three
  exact modular images. This is lookup-count improvement,
  **not** a demonstrated 41-fold elapsed-time speedup.

The actual raw Mojo streams, per-cell source-bound accepted receipts,
nine-cell grid manifest and resource report are preserved in the
[full hosted artifact](https://github.com/larsbx/euler-powers-research/actions/runs/40309437424/artifacts/12643947275).
The green run reports 25,213,056 trials across those cells, but
neither proves global nonexistence nor covers other delta values,
other heights, or `a>64`. The underlying source/replay result is
dated **2026-10-26** and is independent of Braun's much larger
author-reported coverage.

The first bounded novelty-territory grid uses

```text
e in {2,760,001, 2,760,002, 2,760,003}
delta in {1,2,3}
a in [1,64]
c in the complete exact admissible interval for each (e,delta)
b solved exactly with a<=b<=c<=d=e-delta<e.
```

This is **nine complete restricted cells**, NOT a complete search
for any target height. At the end of P14, delta>=4 and a>=65 were unsearched by that experiment.
[P15](POST_BRAUN_FRONTIER.md) now covers selected larger gaps and a=65..256
at e=2,760,001, plus separately labelled signed cells. All other regions remain
unsearched unless explicitly listed in those accepted scopes. The search lies beyond Braun's
*author-reported* nonnegative exhaustive e-bound
`e<=2,760,000`, which our repository has not reproduced.

The dedicated `.github/workflows/discovery-grid.yml` runs
all nine cells under explicit finite resource limits and retains
every native transcript, per-cell exact Python acceptance record,
aggregate grid manifest and GNU-time resource measurement.

## Reproducibility

```sh
pixi run --locked verify
pixi run --locked python tests/test_near_cancellation_stripes.py
pixi run --locked python tests/test_discovery_grid.py
pixi run --locked python tools/search_discovery_grid.py \
  --e-start 2760001 --e-end 2760003 \
  --delta-start 1 --delta-end 3 --a-cap 64 --c-width 4096 \
  --timeout 240 --output benchmarks/results/postbraun-grid-e2760001-2760003-d1-3-a64
```

**No third positive solution is claimed without a full exact
candidate, independent check and fresh published-source comparison.**
A passing zero-witness grid is properly labelled nine parameter-scoped
negative computations. Future work must prioritize genuinely broader
a and delta coverage, resource-normalized throughput and exact
algebraic constructions rather than treating more proof count as the
goal.
