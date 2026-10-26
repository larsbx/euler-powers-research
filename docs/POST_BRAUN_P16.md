# P16 — new minimum summands 257..1024

## Why this region

P15 accepted 176,372,608 exact native trials in 211.02 s including initial
Python replay (maximum RSS 204,304 KiB), plus a fresh 52.84 s full replay.
No primitive identity was found. Its maximum first-summand magnitude was 256.
The accepted P14/P15 evidence remains unchanged in `data/experiments`.

P16 fixes e=2,760,001 and searches only **257<=abs(a)<=1024**:

| First term | Separate delta cells |
| --- | --- |
| Positive | 1, 2, 3, 4, 8, 16, 64, 256 |
| Negative | 4, 16 |

Always require abs(a)<=b<=c<=d=e-delta<e. The negative mode has one negative
term of smallest magnitude. The controller checks disjointness against the
accepted P14/P15 baseline from the coverage index; it never counts regression
reruns as new territory. The ten declared cells contain **318,981,888** exact
(c,abs(a)) trials after the new bound, below a 320,000,000-trial work ceiling.
Each cell covers every possible c using the exact enclosing bounds below.

The former three-term enclosing bound would scan 486,073,344 trials in these
same cells. The new algebraic inequality excludes a prefix containing
167,091,456 pairs that cannot be witnesses. This is a deterministic work-count
reduction, **not a measured runtime speedup**. The measured P15 resources support
this finite experiment; discovery yield is unknown, and no probability claim
is made. Larger minimum summands take priority over another adjacent-height grid.

## Exact bound and proof obligations

Let D=e^5-d^5. For positive a<=A and b<=c:

```
D=a^5+b^5+c^5 <= A^5+2c^5.
```

For a=-u and b<=c:

```
D+u^5=b^5+c^5 <= 2c^5, hence D<=2c^5.
```

For the positive mode, retain the old 3c^5>=D lower bound and intersect it with
2c^5>=D-A^5. For the negative mode, intersect it with 2c^5>=D. Upper bounds
remain c^5<=D (positive) and c^5<=D+A^5 (negative), capped by d. Every root
boundary uses exact integer/BigZ comparisons; no fractional root, limit or
floating approximation enters the search or coverage argument.

`formal/lean/NearCancellationBounds.lean` states the two bounds, prefix
exclusion theorems, and signed upper bound. The full Lean build and axiom audit
must accept these before merge. These mathematical lemmas do not prove native
compiler lowering or the root-search code. Unfiltered small-domain enumeration,
root boundary tests, both known positive native controls, the Scher–Seidl signed
control and independent full arithmetic replay supply separate conformance checks.

## Runtime and certificate contract

The native stripe interface accepts an optional tight-bound flag, producing
`E5STRIPEv3`; old interfaces retain their original c intervals and protocol.
The first-summand resource ceiling rises to 1024. Per-stripe work remains finite:
width<=4096, at most 4,194,304 trials, c<=600,000. Each cell has a 600 s wall
limit; native stripes have 120 s; whole-tree memory is capped by a 2 GiB cgroup
with zero swap and 1200 s service limit; hosted job limit is 30 minutes.

The P16 controller reuses the source-bound native/Python receipt intake and
process-group timeout handling. Its aggregate binds both controller and shared
verifier hashes, the prior coverage-index hash, each child scope and receipt,
raw native stdout, GNU time files and per-stripe native/replay timing. A second
fresh Python process must replay every exact integer result and validate the
aggregate. Output directories use exclusive creation. Partial runs cannot be
promoted to aggregate acceptance.

```sh
pixi run --locked python tests/test_discovery_p16.py
bash scripts/run_research_cgroup.sh /usr/bin/time -v -o p16-resources.txt \
  "$(command -v pixi)" run --locked python tools/search_discovery_p16.py \
  --output benchmarks/results/p16
pixi run --locked python tools/search_discovery_p16.py \
  --verify --output benchmarks/results/p16
```

## Experimental status

**Accepted native execution and full replay, October 26, 2026.**
[Hosted run 40334880575](https://github.com/larsbx/euler-powers-research/actions/runs/40334880575)
completed all ten cells: **318,981,888 exact trials, 965,191 BigZ lookups,
318,016,697 residue/nonpositive rejections, zero primitive positive or signed
identities.** No new identity or global nonexistence claim follows.
All eight implementation workflows passed. Lean built the five new bound lemmas;
the axiom audit accepted 291 total EulerPowers theorems with no nonstandard axioms.
Implementation review/merge provenance is recorded in the evidence PR.

| Stage | Wall seconds | User seconds | System seconds | GNU max RSS (KiB) |
| --- | ---: | ---: | ---: | ---: |
| Native search/controller + initial Python replay | 273.74 | 266.63 | 10.03 | 203,440 |
| Separate fresh-process full Python replay | 103.74 | 101.82 | 1.91 | 110,768 |

Native invocation wall times sum to 170.094627608 seconds (including wrapper,
compile/cache and process startup); initial arithmetic replay sums to
102.935734003 seconds. These are observed resource measurements, not a
controlled same-scope speed comparison.

| First term | delta | abs(a) | Enumerated c interval | Exact trials | BigZ lookups |
| --- | ---: | --- | --- | ---: | ---: |
| positive | 1 | 257..1024 | 170,733..196,119 | 19,497,216 | 29,626 |
| positive | 2 | 257..1024 | 196,120..225,282 | 22,397,184 | 19,908 |
| positive | 3 | 257..1024 | 212,687..244,312 | 24,288,768 | 38,471 |
| positive | 4 | 257..1024 | 225,283..258,781 | 25,727,232 | 69,818 |
| positive | 8 | 257..1024 | 258,782..297,261 | 29,552,640 | 32,553 |
| positive | 16 | 257..1024 | 297,262..341,463 | 33,947,136 | 139,218 |
| positive | 64 | 257..1024 | 392,236..450,560 | 44,793,600 | 68,135 |
| positive | 256 | 257..1024 | 517,544..594,501 | 59,103,744 | 358,205 |
| negative | 4 | 257..1024 | 225,283..258,781 | 25,727,232 | 67,449 |
| negative | 16 | 257..1024 | 297,262..341,463 | 33,947,136 | 141,808 |

Every row has zero primitive witnesses. The old enclosing c prefix is
**algebraically excluded**, not counted as enumerated negative evidence.
Receipts retain both old and new lower bounds and the excluded c count.

The [original accepted ZIP](../data/experiments/p16-run-40334880575.zip),
[byte-identical readable receipt](../data/experiments/p16-accepted.json),
[complete native job log](../data/experiments/p16-run-40334880575-job.log.gz),
[complete formal job log](../data/experiments/p16-formal-run-40334880347-job.log.gz)
and [combined accepted coverage index](../data/experiments/index-p16.json)
are preserved in the repository. ZIP SHA256:
`4de3337ad27b5683abae5e82ef85827dc1e28651b969924cbcc7cd03a9d21d68`.
The download matched the original artifact digest; all 237 files passed ZIP CRC.
Actual source/controller/verifier/prior-index hashes, child receipt hashes,
native transcript/timing hashes, exact cell scopes and aggregate totals checked.

The implementation source head is `9ae7d72dfb53be068a7279c41861258c0f555f4d`;
GitHub tested synthetic merge `05c1f1127fe7d729eaaf3395f056d5cb1090a4b4`.
For archived replay, check out that source head, extract the ZIP, and use
`GITHUB_SHA=05c1f1127fe7d729eaaf3395f056d5cb1090a4b4 GITHUB_RUN_ID=40334880575`
with `tools/search_discovery_p16.py --verify --output EXTRACTED/p16`.
This reproduces metadata; actual source hashes and every arithmetic result are
still checked. It is not a new native execution attestation.

The old `index.json` is unchanged because its hash is an accepted experimental
input. `index-p16.json` supersedes it for current combined coverage.

Unsearched outside accepted scopes: unlisted delta values, larger first summands,
other high target heights, and general signed orderings (including abs(a)>b).
Even successful completion of this experiment would not be a complete height
census. A candidate needs exact identity, five-way gcd, equivalence comparison
against the known registry and fresh literature review before a discovery claim.

## Current union and next unexecuted work

Across P14/P15/P16, e=2,760,001 now has complete restricted positive coverage
for a=1..1024 at delta=1,2,3,4,8,16,64,256. The supported signed mode covers
abs(a)=1..1024 at delta=4,16, and only 1..256 at delta=64. General signed
orderings and every unlisted gap remain open, as do other high target heights
outside the explicitly accepted P14 cells. This is not a complete height census.

Next budgeted candidates are untouched positive gaps (for example 5..7 or
9..15) at the new cap, or a>=1025 after reviewing an increased per-stripe ceiling.
Use per-cell timings and lookup counts; no fixed residue rejection factor or
probability of finding a solution is assumed. These next regions are not yet
searched or accepted.
