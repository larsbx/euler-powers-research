# P19: larger minimum summands and exact residue-first evaluation

New finite domain: `e=2,760,001`, `1025<=abs(a)<=4096`, with ordered
`abs(a)<=b<=c<=d<e`, `d=e-delta`. Six positive gaps are searched and one
supported signed gap. Every cell is disjoint from immutable accepted
`data/experiments/index-p18.json`; the current ledger is not modified by plans.

| First term | delta | c minimum | c maximum | Exact (c,abs(a)) trials |
| --- | ---: | ---: | ---: | ---: |
| positive | 1 | 170733 | 196119 | 77988864 |
| positive | 2 | 196120 | 225282 | 89588736 |
| positive | 3 | 212687 | 244312 | 97155072 |
| positive | 4 | 225283 | 258781 | 102908928 |
| positive | 8 | 258782 | 297261 | 118210560 |
| positive | 16 | 297262 | 341463 | 135788544 |
| negative | 4 | 225283 | 258781 | 102908928 |

Planned work: **724,549,632** trials, below an 800,000,000 review ceiling.
The c bounds are exact integer roots of the existing proved inequalities:
`D<=4096^5+2*c^5` for positive a, `D<=2*c^5` for negative a, and
`c^5<=D` / `c^5<=D+4096^5`, respectively, with `D=e^5-d^5`.
The legacy enclosing bound `D<=3*c^5` remains intersected with the lower
bound. All enumerated trials and impossible prefixes remain distinct.

The native and Python intake cap rises from 1024 to 4096; c, target-height,
gap, stripe-width, timeout and physical-memory policies are unchanged.
The legacy multi-height grid keeps an explicit 1024 cap, preserving its
original resource contract when the shared stripe cap increases.
Small-height tests explicitly exercise `A>c_end`, where the a residue cache
must stop at the actual power table's endpoint. The search remains limited
to the declared ordering; general signed `abs(a)>b` is not covered.

## Computation moved, no necessary condition changed

Before P19, every trial constructed the exact BigZ candidate and then
reduced it modulo 99000, 41 and 61. Now each a's exact fifth-power residues
are cached, and each c's `left=D-c^5` is reduced once. For each modulus m:

```text
positive a: residue = (left_mod + m - a5_mod) % m
negative a: residue = (left_mod + a5_mod) % m
```

Only trials passing all three existing bounded b-image gates construct a
BigZ complement, test positivity and perform the unchanged exact binary
fifth-power membership and primitive-gcd checks. Combined reject counters,
lookup counts, witness order and transcript protocol remain unchanged.
The intermediate residue expressions lie in `[0,198000)`, so machine
arithmetic cannot overflow. All fifth powers and candidate identities still
use the pinned BigZ implementation. There are no new probabilistic filters.

Five Lean statements in `ResidueFirst.lean` prove the modular identities,
small-intermediate bounds and Boolean guard commutation. These do not prove
the native compiler, BigZ library or residue-image implementation. Native
conformance includes unfiltered small-domain controls and full independent
Python reconstruction of all search trials.

## Same-workload comparison before promotion

`benchmarks/native/stripe_before_p19.mojo` preserves the accepted pre-P19
algorithm with **only** its A policy guard relaxed to 4096. Replacing that
guard with 1024 reproduces original source SHA-256
`365a415ea60b9270b0c5845663e42dc6f55b9dd67680f66e001b47fbc9c1227d`.
The benchmark checks that fingerprint before running.

Both versions are compiled once. Three full 4096-c production stripes,
each with a=1025..4096, are compared with three interleaved repetitions:
positive delta=1, negative delta=4, positive delta=16. Three calibration
stripes retain Lander-Parkin, Frye and Scher-Seidl controls at A=4096.
There are 24 timed native process invocations in total. Every observed raw
transcript must equal an independent Python oracle exactly, and a separate
fresh process replays every case. The benchmark receives zero new Euler
discovery credit because its subsets are not full independent discovery cells.

This workload caches exact powers and bounded residue images within each
production stripe, as the controller does. Process startup and table creation
are included; compiler time is measured separately. Measurements apply to
these declared stripes only and do not establish a universal speedup.
The pair-sum reconstruction algorithm is not used by this experiment.

## Resources and replay

The accepted P18 batch took 575.79 seconds including initial Python replay
for 786,334,720 trials, followed by a 237.46-second fresh replay. This supports
the bounded P19 workload without relying on an optimization speedup.
Every search/replay/comparison process tree has 2 GiB physical memory,
zero swap and 1200 seconds; stripes are at most 4096 c values with 120-second
timeouts and each full cell has a 600-second timeout. The job limit is
35 minutes, including comparison, calibration, search, fresh replay and uploads.

```sh
pixi run --locked python tests/test_discovery_p19.py
pixi run --locked python tests/benchmark_residue_first.py --output /tmp/residue-first-new
pixi run --locked python tests/benchmark_residue_first.py --verify --output /tmp/residue-first-new
pixi run --locked python tools/search_discovery_p19.py --output /tmp/p19-new
pixi run --locked python tools/search_discovery_p19.py --verify --output /tmp/p19-new
```

Status: planned, not yet accepted. Hosted acceptance will bind the original
comparison and search transcripts, every source/receipt hash, finite coverage
addition, source/run labels and explicit runtime/RSS measurements. Original
artifacts and all measured outcomes will be preserved, including negative
or mixed performance outcomes. A zero-witness result would apply only to
these seven finite cells, not any full target height or global domain.
