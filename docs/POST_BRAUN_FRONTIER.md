# P15 — broader gaps, larger minimum summands, and a signed frontier

The October 26 request accepts either a new primitive strictly positive identity
(the third known positive class) or a genuinely new signed identity (the fifth
class relative to the four-entry source registry). Signed discoveries are never
counted as positive solutions. The positive objective remains primary.

## Baseline and selection rationale

PR #46 was merged at `0ba6bf59e4be53f1f1444122c053a0ea1881908d` after all
six latest-head workflows passed. Its clean code review covers `3316013`;
head `2565882` adds only the measured-result documentation, reviewed against
the run logs and archived evidence. Latest-head grid run **40310016033**:
25,213,056 trials, 56,409 exact lookups, no primitive positive witnesses.
GNU time: **95.90 s wall, 91.82 s user, 7.87 s system, 272,920 KiB maximum RSS**.
The aggregate includes controllers, native invocations and Python replays;
it is not a native-only benchmark. Rejection/lookup counts are mathematical
operation counts, not measured speedup factors.

The accepted full original artifact is preserved durably as
[`p14-run-40310016033.zip`](../data/experiments/p14-run-40310016033.zip).
Original GitHub artifact: [12644088071](https://github.com/larsbx/euler-powers-research/actions/runs/40310016033/artifacts/12644088071).
ZIP SHA256: `0557f355447acc51e8edd59c443f63a8aeed79aae3ba0602f5f248f231761c63`.
This archive preserves original transcripts and original receipts without
rewriting their format or source identities.

The measured memory margin and per-cell rejection counts support trying up to
256 magnitudes and geometrically spaced larger gaps at one height, rather than
repeating adjacent heights with a<=64. This is an explicit exploration heuristic,
not a probability model for discovery. There is no proven ranking by discovery
yield. The 11 selected cells have **176,372,608** exact (c,abs(a)) trials,
below a reviewed 180,000,000-trial ceiling. Every one is disjoint from P14.

All new cells fix **e=2,760,001**, **d=e-delta**, with the full rigorous enclosing
c interval and **abs(a)<=b<=c<=d<e**. Positive b is solved exactly.

| First summand | delta values (separate cells) | abs(a) interval | Trials across group |
| --- | --- | --- | ---: |
| Positive | 4, 8, 16, 64, 256 | 1..256 | 98,095,872 |
| Positive | 1, 2, 3 | 65..256 | 25,213,056 |
| Negative | 4, 16, 64 | 1..256 | 53,063,680 |

The negative mode covers **one negative term of smallest absolute magnitude**.
It does not cover general signed identities, two negative summands, or negative
terms larger in magnitude than b. In particular it does not rediscover Braun's
identity within this small-magnitude domain. Scher–Seidl is the signed native
calibration: (-220,5027,6237,14068,14132).

## Finite coverage argument and execution

For positive a, D=e^5-d^5=a^5+b^5+c^5 implies c^5<=D<=3c^5.
For negative a=-u with u<=b<=c, D=-u^5+b^5+c^5 implies
D<=2c^5<=3c^5 and c^5<=D+u^5<=D+A^5.
Thus the old exact lower bound still encloses every candidate; the negative
upper bound is enlarged to floor_fifth_root(D+A^5), capped by d.
These are safe enclosing intervals, not assertions that every pair in them
can extend to an identity. No floating arithmetic enters bounds or identities.

The existing native Mojo kernel accepts optional A_MIN and sign, preserves its
legacy positive interface, and keeps complete bounded b fifth-power images
modulo 99000, 41, 61. Exact BigZ binary lookup, equality and gcd decide admission.
The Python hash-power implementation separately rebuilds every complete
transcript. Unfiltered brute enumeration checks its bounds and filters over
small positive and signed domains. Positive and signed known-witness native
calibration plus minimum-summand exclusion test cover both search modes.

`tools/search_discovery_frontier.py` supplies a deterministic 11-cell controller,
rejects overlap/P14 repeats, enforces the work ceiling, and permits 600 seconds
per cell (120 seconds per native stripe). A cell timeout kills its entire
process group and cannot publish aggregate acceptance. Hosted execution limits
each process to 2 GiB virtual address space and the job to 30 minutes.
Fresh output directories prevent modification of prior accepted evidence.

Each stripe preserves native stdout, raw GNU time output, wall time in integer
nanoseconds, Python replay time, CPU seconds, maximum native invocation RSS,
and hashes binding all these records. Timing includes the pinned Mojo wrapper
and any compile/cache overhead; it is not kernel-only timing. The aggregate
also measures total controller/replay wall/CPU/RSS. A second fresh Python process
replays all exact arithmetic and checks receipts, scope, source hashes, complete
coverage, totals, witnesses and resources before workflow success. Receipts bind
the kernel, bridge, wrapper, lockfile, verifier, registry and immutable shared
arithmetic pin. Sources and execution run are recorded without implying a
cryptographic remote attestation.

```sh
pixi run --locked python tests/test_discovery_frontier.py
ulimit -v 2097152
/usr/bin/time -v -o frontier-resources.txt \
  pixi run --locked python tools/search_discovery_frontier.py --output benchmarks/results/frontier
pixi run --locked python tools/search_discovery_frontier.py --verify --output benchmarks/results/frontier
```

## Status and remaining regions

**Planned; no P15 computation is accepted until the hosted native run and
independent full replay succeed.** The workflow archives all evidence, including
partial failed output distinctly from accepted aggregate results. Accepted
results and measured resource totals will be recorded here after execution.

Unsearched: other heights, gaps not listed, a>256, the larger summand intervals
at e=2,760,002 and 2,760,003, and the general signed domain. Even after all 11
cells pass, no complete height census or global nonexistence statement follows.
Any candidate needs exact identity, primitivity, equivalence normalization,
comparison with all four known classes, and fresh primary-source literature
review before a discovery claim. A signed candidate cannot be called a third
positive example.
