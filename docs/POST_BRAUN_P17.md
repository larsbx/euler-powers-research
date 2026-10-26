# P17 — close the positive delta=1..16 block and log every accepted cell

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

**Planned.** No P17 negative result or discovery is claimed until actual native
execution, complete independent replay and evidence checks pass. Accepted
results will retain exact per-cell bounds, excluded prefixes, trials, rejections,
lookup counts, native transcripts, source receipts, resources and coverage unions.
Any new witness requires exact identity, primitivity, known-class equivalence and
fresh literature review before a discovery claim. Regions outside the listed
cells remain unsearched unless separately backed by accepted repository evidence.
