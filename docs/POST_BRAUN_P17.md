# P17 — close the positive delta=1..16 block and log every accepted cell

**Current territory has advanced:** [P18](POST_BRAUN_P18.md) completed gaps 17..32. This document preserves the historical P17 plan and results; use the [current map](../data/experiments/TERRITORY.md) for the accepted union.

P16 measured 318,981,888 exact trials in 273.74 s including initial replay,
maximum RSS 203,440 KiB; fresh full replay took 103.74 s. Its accepted coverage
leaves ten positive gaps missing from the e=2,760,001, a<=1024 block:
**delta=5,6,7,9,10,11,12,13,14,15**. P17 searches exactly these untouched cells.

Every cell fixes e=2,760,001, d=e-delta, 1<=a<=1024 and a<=b<=c<=d<e.
The exact two-term bound and modular filters are unchanged from P16. All
possible c are covered by the enclosing interval, with the impossible prefix
separately justified by the existing Lean inequalities. Work is
**409,884,672 exact (c,a) trials**, below a reviewed 420,000,000 ceiling.
Completing P17 would establish restricted positive coverage at every gap
1..16 for a<=1024 at this one target height; it would not exhaust the height.

The measured P16 throughput supports this bounded next experiment without
assuming a fixed rejection factor, probability of discovery or runtime speedup.
Resource controls stay at 600 s/cell, 120 s/native stripe, 2 GiB whole-process
physical-memory cgroup, zero swap, 1200 s/service and a 30-minute hosted job.

## Cumulative territory logging

`tools/coverage_ledger.py` normalizes accepted P14/P15/P16 cells, rejects
intersecting or repeated a intervals at the same (e,delta,sign), and coalesces
adjacent intervals for a readable coverage map. Complete positive height
censuses are a separate category, never merged with restricted cells or signed
coverage. Counts from full-height pair-index algorithms use different trial
units and are not added to high-height (c,abs(a)) counts.

The P17 planner reads the immutable accepted `index-p16.json`, derives the
missing gaps and checks the exact expected ten-cell plan. Planned, partial,
foreign-source, altered and repeated receipts cannot be promoted into the
cumulative log. The completed native directory receives `coverage-addition.json`
only after source/receipt/transcript/time hashes, exact scopes, totals and
witnesses agree. A second fresh process replays **all** integer arithmetic and
recomputes that addition byte-for-byte. It binds the prior ledger, controller,
shared verifier and ledger-code hashes. Existing accepted inputs remain unchanged.

This is source-backed computation evidence, not cryptographic remote-worker
attestation. SHA-256 checks integrity. Final publication adds archive/run metadata
to the verified addition and writes a new ledger, retaining its predecessor.
Historical repeated runs and calibration-only tests are recorded separately
from new territory. Algebraically excluded c values are not enumerated trials.

## Execute and inspect

```sh
pixi run --locked python tests/test_coverage_ledger.py
bash scripts/run_research_cgroup.sh /usr/bin/time -v -o p17-resources.txt \
  "$(command -v pixi)" run --locked python tools/search_discovery_p17.py \
  --output benchmarks/results/p17
pixi run --locked python tools/search_discovery_p17.py \
  --verify --output benchmarks/results/p17
pixi run --locked python tools/coverage_ledger.py \
  --ledger data/experiments/index-p16.json --markdown
```

## Status

**Accepted on October 26, 2026.** [Native run 40340932947](https://github.com/larsbx/euler-powers-research/actions/runs/40340932947)
completed all ten cells, fresh full arithmetic replay and byte-identical cumulative
log replay: **409,884,672 trials, 937,235 BigZ lookups, 408,947,437 residue/nonpositive
rejections, zero primitive positive identities.** All six latest-head workflows
passed, automated code review was clean, and PR #51 merged at
`99f0aedd9d75be7acd2537b4f1bae9ea4a05335a`.

| Stage | Wall seconds | User seconds | System seconds | GNU max RSS (KiB) |
| --- | ---: | ---: | ---: | ---: |
| Search/controller + initial Python replay | 293.19 | 286.37 | 9.62 | 182,036 |
| Separate fresh-process full replay | 116.52 | 114.80 | 1.71 | 70,620 |

Native invocation wall times sum to 174.740183648 s (wrapper, process startup
and compile/cache costs included); initial Python replay sums to 117.685242539 s.
These measurements do not establish a same-scope algorithmic speedup.

Every row below has zero primitive witnesses, with 1<=a<=1024.

| delta | Enumerated c (inclusive) | Exact trials | BigZ lookups |
| ---: | --- | ---: | ---: |
| 5 | 235,565..270,592 | 35,868,672 | 106,745 |
| 6 | 244,313..280,641 | 37,200,896 | 142,725 |
| 7 | 251,962..289,428 | 38,366,208 | 68,271 |
| 9 | 264,950..304,347 | 40,343,552 | 34,381 |
| 10 | 270,592..310,828 | 41,202,688 | 86,503 |
| 11 | 275,800..316,810 | 41,995,264 | 237,082 |
| 12 | 280,641..322,371 | 42,732,544 | 14,516 |
| 13 | 285,170..327,573 | 43,421,696 | 84,261 |
| 14 | 289,428..332,465 | 44,070,912 | 58,477 |
| 15 | 293,450..337,084 | 44,682,240 | 104,274 |

The original accepted [ZIP](../data/experiments/p17-run-40340932947.zip),
[aggregate receipt](../data/experiments/p17-accepted.json),
[coverage-addition receipt](../data/experiments/p17-coverage-addition.json) and
[complete job log](../data/experiments/p17-run-40340932947-job.log.gz) are permanent.
ZIP SHA256: `c83bb4c5165b5ba5e00024fc2b01247ceb8048fed4424c664be3b8296308dd97`.
All 230 ZIP files passed CRC; downloaded source/controller/verifier/ledger-code,
predecessor, child receipt, transcript/time hashes, scopes, totals, cumulative
addition and interval union were checked again.

Implementation source: `7151330d011de99e8831ff3d6742d4bb37bd10a1`;
GitHub tested synthetic merge `f03f38fc486e5969486a07329e4c2ea037565e8a`.
Archived replay uses that source snapshot, extracted ZIP and
`GITHUB_SHA=f03f38fc486e5969486a07329e4c2ea037565e8a GITHUB_RUN_ID=40340932947`
with `tools/search_discovery_p17.py --verify --output EXTRACTED/p17`.
This reproduces source metadata; actual hashes and every integer result still
receive independent checks. It does not assert a new native execution.

## Cumulative map and historical inventory

The current pointer is [current.json](../data/experiments/current.json), selecting
[index-p17.json](../data/experiments/index-p17.json) by hash. The human-readable
[territory map](../data/experiments/TERRITORY.md) is generated from the ledger.

The accepted P14/P15/P16/P17 union contains **40 disjoint high-height cells**,
**930,452,224 exact (c,abs(a)) trials** and **2,483,121 BigZ lookups**. Positive
coverage at e=2,760,001 now includes delta=1..16,64,256 with a=1..1024.
The supported signed mode covers delta=4,16 with abs(a)<=1024 and delta=64
with abs(a)<=256. At e=2,760,002 and 2,760,003 only the P14 positive gaps
1..3 with a<=64 are accepted.

The **full positive e=2..320 census** is a separate category. Its original
[80-shard ZIP](../data/experiments/b320-run-40334880431.zip) and
[crosscheck](../data/experiments/b320-accepted-crosscheck.json) are preserved.
Its 5,201,461 positive-complement right-pair visits and one known primitive
Lander-Parkin witness are not added to high-height (c,abs(a)) totals.
Fresh Python replay of all downloaded shards and B144/B256/B320 reconciliation
reproduced the original crosscheck exactly. B320 ZIP SHA256:
`fb9f1e4f4c106a45b00d5575c1c20a33c0c29f79855c79df30380b0105ba9995`.

The inventory also records native/Python test-covered calibration cells at
144, 85,359, 85,360 and signed 14,132, with source/test/log provenance. These
remain a separate evidence class from accepted per-cell discovery receipts.
[Archived validation output](../data/experiments/validation-run-40334880418-job.log.gz)
retains the exact printed scopes, counts and known-witness results. Earlier
B12/B144/B256 runs are subsumed by B320; P13's first cell is subsumed by P14.
No repeat receives new territory credit. External author-reported bounds are
listed as unreproduced claims, never as this program's accepted territory.

Unlisted gaps, larger first summands, other high target heights and general
signed orderings remain open. Next positive candidates begin at delta=17 at
e=2,760,001 under the same a cap, or at a>=1025 after a separate resource review.
They have not been searched here. No complete high-height or global
nonexistence claim is made.
