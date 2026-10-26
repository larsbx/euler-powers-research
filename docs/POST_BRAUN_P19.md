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

## Accepted native computation

[Latest-head run 40358860783](https://github.com/larsbx/euler-powers-research/actions/runs/40358860783)
completed all seven cells and a separate fresh full Python arithmetic replay:
**724,549,632 trials, 1,620,700 exact BigZ lookups, 722,928,932 modular/nonpositive
rejections and zero primitive identities**. The coverage addition replay was
byte-identical. The current source is
`dd8fe2e43f88287fcfbc190938aa0947212475a0`, tested synthetic PR merge
`5b733864503f48125fbdb0aae08c08f9a25ac58a`; source acceptance is tracked in
[PR #57](https://github.com/larsbx/euler-powers-research/pull/57).

| Process | Wall seconds | User seconds | System seconds | Maximum RSS KiB |
| --- | ---: | ---: | ---: | ---: |
| Search plus initial independent replay | 146.66 | 143.35 | 4.01 | 179,264 |
| Separate fresh full replay | 107.10 | 106.46 | 0.62 | 69,852 |
| Before/after comparison and initial oracle | 21.67 | 22.59 | 0.35 | 249,836 |
| Separate comparison replay | 5.95 | 5.90 | 0.05 | 69,644 |

Native search invocation wall times sum to 39.168890845 seconds; initial
Python replays sum to 107.080743872 seconds. Native invocation times include
wrapper/process/compile overhead. Differences from P18 whole-batch timings
cannot be attributed solely to the optimization: the cells, c counts, a
ranges, process counts and hosts differ. The same-workload comparison below
is the evidence for the measured native improvement.

### Before/after production stripes

All 24 native transcripts agreed with the independent oracle exactly,
including lookup counts and published primitive calibration witnesses.
Each production row below enumerated 12,582,912 trials per invocation.
Times are medians of three interleaved precompiled process invocations.

| Sign | delta | c interval | Before seconds | After seconds | Before/after ratio |
| --- | ---: | --- | ---: | ---: | ---: |
| positive | 1 | 170733..174828 | 1.030583689 | 0.134256195 | 7.68 |
| negative | 4 | 225283..229378 | 1.663767633 | 0.175002351 | 9.51 |
| positive | 16 | 319362..323457 | 1.149558807 | 0.193946801 | 5.93 |

The result establishes lower measured native process times on these three
sample stripes, not a universal or whole-search speedup ratio. Power caches
and bounded images are constructed within every process as in production.
Compiler time is excluded and recorded separately: before 1.79 seconds /
249,836 KiB RSS, after 0.86 seconds / 177,352 KiB RSS. Maximum query RSS was
50,620 KiB before and 48,528 KiB after. These memory observations are sample
measurements, not a guaranteed memory reduction. The standalone binary
hashes are recorded; executable bytes are temporary build output.

Per-cell accepted totals:

| Sign | delta | Trials | BigZ lookups | Primitive witnesses |
| --- | ---: | ---: | ---: | ---: |
| positive | 1 | 77,988,864 | 126,730 | 0 |
| positive | 2 | 89,588,736 | 76,041 | 0 |
| positive | 3 | 97,155,072 | 150,813 | 0 |
| positive | 4 | 102,908,928 | 283,751 | 0 |
| positive | 8 | 118,210,560 | 127,233 | 0 |
| positive | 16 | 135,788,544 | 573,909 | 0 |
| negative | 4 | 102,908,928 | 282,223 | 0 |

### Permanent evidence and replay

The original 195-file [ZIP](../data/experiments/p19-run-40358860783.zip)
(artifact `12667282649`) includes the full search and before/after native
transcripts, per-process time files, accepted receipts and outer resource
reports. ZIP SHA-256:
`f58f471cc27b6aa307495546b8e97ecaeb6ea94aec9a19903cf5ee4ecb224694`.
The [search receipt](../data/experiments/p19-accepted.json),
[coverage addition](../data/experiments/p19-coverage-addition.json),
[comparison receipt](../data/experiments/p19-residue-first-accepted.json),
[native log](../data/experiments/p19-run-40358860783-job.log.gz) and
[formal log](../data/experiments/p19-formal-40358860941-job.log.gz) are preserved.
Pinned hosted Lean 4.34.1 built the five new statements and audited 355
kernel-checked theorems, including generated auxiliaries, with no
nonstandard axioms. Native compiler/library lowering is not formally proved.

After download, ZIP SHA/CRC, all bound source/controller/verifier/ledger/
predecessor, child/transcript/time hashes, exact scopes/counts/resources
and byte-identical cumulative addition passed intake checks. The comparison
also passed another complete local independent arithmetic replay. Every
benchmark CERT was a known calibration identity. The full 724-million-trial
search arithmetic replay was performed in the separate hosted Python process;
downloaded intake did not redundantly repeat all search arithmetic.

Historical replay checks out the recorded source, extracts the ZIP and uses
`GITHUB_SHA=5b733864503f48125fbdb0aae08c08f9a25ac58a GITHUB_RUN_ID=40358860783`
with `tools/search_discovery_p19.py --verify --output EXTRACTED/p19`.
Comparison replay uses `tests/benchmark_residue_first.py --verify --output
EXTRACTED/residue-first`. Environment labels reproduce metadata while actual
source hashes and all replayed arithmetic are checked; this is not a signed
remote-worker attestation.

The earlier source-head run `40358563573` also completed comparison/search/
fresh replay, but a separate legacy-grid resource-contract test failed on
that head. Its original [195-file ZIP](../data/experiments/p19-superseded-40358563573.zip)
and [job log](../data/experiments/p19-superseded-40358563573-job.log.gz) are
retained as superseded validation. ZIP SHA-256:
`94bb0cecc77310ff710894ec289245980ccf690608a9c22ca42cc4871127c888`.
Source head `3682f13cee895456a9559f467f89bf21065117cc` tested synthetic merge
`846de7cf5c9617f7cc7535a8059b0c6d528efa13`. The fix explicitly retains the
legacy grid's 1024 cap. Sources relevant to P19 arithmetic/comparison and
all search scopes/counts/witnesses agree between the runs. The repeat gets
**zero duplicate discovery credit**. It is not a second independent region.

## Current territory and remaining work

The [current map](../data/experiments/TERRITORY.md) and hashed pointer now
select `index-p19.json`: **63 disjoint high-height cells, 2,441,336,576 exact
trials and 5,444,245 BigZ lookups**. Immutable index-p18 and earlier raw
archives are retained. Positive e=2,760,001 now has a<=4096 at gaps
1,2,3,4,8,16, and a<=1024 at the other accepted gaps through 32 plus 64/256.
Supported signed delta=4 extends abs(a) through 4096; delta=16 and delta=64
retain their prior smaller caps. Neighboring-height P14 cells are unchanged.

Minimum summands >=4097 at the expanded gaps, >=1025 at the other gaps,
unlisted cancellation gaps, other high target heights, and general signed
abs(a)>b/multiple-negative orderings remain open. No full-height or global
nonexistence claim follows. Benchmarks, superseded runs, B320, calibration
and external reports remain separate from unique high-height trial totals.
