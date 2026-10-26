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
the whole process tree to 2 GiB physical memory (systemd MemoryMax, zero swap) and the job to 30 minutes.
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
bash scripts/run_research_cgroup.sh /usr/bin/time -v -o frontier-resources.txt \
  "$(command -v pixi)" run --locked python tools/search_discovery_frontier.py --output benchmarks/results/frontier
pixi run --locked python tools/search_discovery_frontier.py --verify --output benchmarks/results/frontier
```

## Status and remaining regions

**Accepted on October 26, 2026.** [Hosted run 40329902748](https://github.com/larsbx/euler-powers-research/actions/runs/40329902748)
completed all 11 cells and the fresh-process independent full replay:
**176,372,608 trials, 524,286 exact lookups, 175,848,322 residue/nonpositive
rejections, and zero primitive positive or signed witnesses.** All seven
latest-head workflows passed; latest-head code review on `9d6dd4c` was clean.
Implementation PR #47 merged at `d48f9752ac3bb7f81eec78e5752dba647dc51bb3`.

The [original accepted ZIP](../data/experiments/p15-run-40329902748.zip),
[readable aggregate receipt](../data/experiments/p15-accepted-frontier.json),
[complete compressed job log](../data/experiments/p15-run-40329902748-job.log.gz)
and [archive/coverage index](../data/experiments/index.json) are preserved in
the repository. ZIP SHA256:
`bd09635a09176bbf3f0671492af8f8ce21a7fec0abf07c147dd54cc572a53ea2`.
All 387 artifact files, source hashes, native transcript/timing hashes, receipt
hashes, totals and exact scopes were checked again after download.

| Stage | Wall seconds | User seconds | System seconds | GNU max RSS (KiB) |
| --- | ---: | ---: | ---: | ---: |
| Search/controller + initial per-stripe replay | 211.02 | 199.53 | 13.84 | 204,304 |
| Separate fresh-process complete Python replay | 52.84 | 50.34 | 2.49 | 110,708 |

Native invocation wall times sum to **158.358636741 s** (including wrapper,
compile/cache and process startup); initial Python arithmetic replay sums to
**52.005780444 s**. Neither number is a controlled same-scope speed comparison.
The job log separately preserves systemd cgroup charge accounting; GNU RSS
and cgroup charged-memory peaks use different accounting and are not equated.

Every row below has **zero primitive witnesses**. c intervals are inclusive,
with abs(a)<=b<=c<=d and b solved exactly.

| First term | delta | abs(a) | c interval | Exact trials | BigZ lookups |
| --- | ---: | --- | --- | ---: | ---: |
| positive | 4 | 1..256 | 207,735..258,781 | 13,068,032 | 29,231 |
| positive | 8 | 1..256 | 238,625..297,261 | 15,011,072 | 14,572 |
| positive | 16 | 1..256 | 274,108..341,463 | 17,243,136 | 74,472 |
| positive | 64 | 1..256 | 361,684..450,560 | 22,752,512 | 35,821 |
| positive | 256 | 1..256 | 477,232..594,501 | 30,021,120 | 189,335 |
| positive | 1 | 65..256 | 157,434..196,119 | 7,427,712 | 12,836 |
| positive | 2 | 65..256 | 180,844..225,282 | 8,532,288 | 7,007 |
| positive | 3 | 65..256 | 196,120..244,312 | 9,253,056 | 14,055 |
| negative | 4 | 1..256 | 207,735..258,781 | 13,068,032 | 39,362 |
| negative | 16 | 1..256 | 274,108..341,463 | 17,243,136 | 74,172 |
| negative | 64 | 1..256 | 361,684..450,560 | 22,752,512 | 33,423 |

The PR source head is `9d6dd4cc98905c29c0829e4684d6673076d505dc`;
GitHub ran its synthetic test merge `144b19eac6cee9a0724d0b3bd14902e2f63ed261`,
recorded in receipts. Source-file hashes agree with that implementation.
For archived arithmetic replay, check out the recorded source head, extract the
original ZIP and set `GITHUB_SHA=144b19eac6cee9a0724d0b3bd14902e2f63ed261`
and `GITHUB_RUN_ID=40329902748` when invoking the controller's `--verify` mode
on the extracted `frontier` folder. These environment values reproduce metadata;
they are not a new execution attestation. The verifier still checks actual source
hashes and independently recomputes all finite arithmetic.

Outside the explicit P14/P15 union, unsearched regions include all other high
target heights, unlisted gaps at e=2,760,001, a>256, a>=65 at e=2,760,002
and 2,760,003, and the general signed domain. Completion of these 11 cells
does not give a complete height census or global nonexistence statement.
Any candidate needs exact identity, primitivity, equivalence normalization,
comparison with all four known classes, and fresh primary-source literature
review before a discovery claim. A signed candidate cannot be called a third
positive example.

The initial run 40329491348 passed native positive/signed calibration but failed
before accepting any search cell: a 2 GiB RLIMIT_AS blocked tcmalloc
1 GiB-aligned virtual reservations. The revised workflow uses a 2 GiB physical
memory cgroup instead, with zero swap and a 1,200 s whole-tree service limit.
That failed attempt is not a negative mathematical search result.

## Next proof/computation obligations (not executed)

The measured lookup rate varies substantially by cell (14,572 lookups at
positive delta=8 versus 189,335 at delta=256); do not assume a fixed rejection
factor. Next prioritize untouched intervals or larger minimum summands, using
per-cell timings to budget them. A useful exact optimization before raising
the cap: positive a<=A implies D<=A^5+2c^5, and negative a implies D<=2c^5.
Prove/test these tighter c lower bounds against unfiltered enumeration and
known witnesses before using the saved work for a>=257 or missing gaps.
General signed searches also need a new ordering contract to admit negative
terms larger than b. None of these proposals is accepted coverage.
