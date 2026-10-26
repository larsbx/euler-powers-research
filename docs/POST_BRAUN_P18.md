# P18: untouched positive cancellation gaps 17..32

**Current territory has advanced:** [P19](POST_BRAUN_P19.md) extends selected minimum-summand ranges to 4096. The P18 source, predecessor and results below remain historical evidence; see the [current map](../data/experiments/TERRITORY.md).

Fixed scope: `e=2,760,001`, each `delta=e-d` in `17..32`,
`1<=a<=1024`, `a<=b<=c<=d<e`. These sixteen cells are disjoint from
the accepted immutable P17 predecessor `data/experiments/index-p17.json`.
No new pruning rule is used. The cyclotomic work is a separate algorithm
development track and receives no credit for this search.

For `D=e^5-d^5`, every solution satisfies `D<=1024^5+2*c^5`
and `c^5<=D`. Integer binary searches give complete enclosing intervals;
the omitted lower prefix is impossible by the existing Lean bounds.
Every `(c,a)` in each declared interval is visited and independently replayed.

| delta | c minimum | c maximum | exact (c,a) trials |
| ---: | ---: | ---: | ---: |
| 17 | 300888 | 345628 | 45814784 |
| 18 | 304347 | 349602 | 46342144 |
| 19 | 307656 | 353403 | 46845952 |
| 20 | 310828 | 357047 | 47329280 |
| 21 | 313876 | 360548 | 47793152 |
| 22 | 316810 | 363918 | 48239616 |
| 23 | 319639 | 367168 | 48670720 |
| 24 | 322372 | 370307 | 49086464 |
| 25 | 325014 | 373342 | 49488896 |
| 26 | 327574 | 376282 | 49878016 |
| 27 | 330056 | 379133 | 50255872 |
| 28 | 332465 | 381901 | 50623488 |
| 29 | 334806 | 384591 | 50980864 |
| 30 | 337084 | 387207 | 51326976 |
| 31 | 339302 | 389755 | 51664896 |
| 32 | 341463 | 392237 | 51993600 |

Total planned work is **786,334,720** exact trials, below an 800,000,000
review ceiling. P17 measured 409,884,672 trials in 293.19 seconds including
initial Python replay, followed by a 116.52-second fresh replay. These
measurements support this bounded larger batch; they do not guarantee a
runtime or a discovery probability. Each native stripe is at most 4096 c
values and has a 120-second timeout; each cell has a 600-second timeout.
The entire search and each separate replay run in the existing 2 GiB
physical-memory, zero-swap cgroup with a 1200-second service limit.

```sh
pixi run --locked python tests/test_discovery_p18.py
pixi run --locked python tools/search_discovery_p18.py --output /tmp/p18-new
pixi run --locked python tools/search_discovery_p18.py --verify --output /tmp/p18-new
```

The controller issues source-bound child and aggregate receipts, and a
coverage addition only after native/Python agreement. A separate full
replay recomputes every transcript and the exact coverage addition.
`coverage_ledger.certified_addition` now accepts the reviewed experiment
ID P18 explicitly; its default remains P17, preserving existing behavior.
Historical evidence replay still requires its archived source snapshot.

## Accepted result

Accepted on October 26, 2026. [Native run 40352704602](https://github.com/larsbx/euler-powers-research/actions/runs/40352704602)
passed all sixteen cells and a separate fresh full Python arithmetic replay:
**786,334,720 exact trials, 1,340,424 BigZ lookups, 784,994,296 modular/nonpositive
rejections, zero primitive positive identities**. The fresh process also
recomputed the coverage addition byte-for-byte. All seven source-head
workflows passed, review had no findings, and PR #54 merged at
`631490a18031b0419c793daddf55f4b0eeaa6610`.

| Process | Wall seconds | User seconds | System seconds | Max RSS KiB |
| --- | ---: | ---: | ---: | ---: |
| Search plus initial Python replay | 575.79 | 562.40 | 18.87 | 184,180 |
| Separate fresh full replay | 237.46 | 234.12 | 3.31 | 93,496 |

Native invocation wall times sum to 340.694402985 seconds (wrapper/startup/
compile costs included); initial Python replays sum to 233.838480872 seconds.
No same-scope speedup is inferred from these new cells.

The original 428-file [ZIP](../data/experiments/p18-run-40352704602.zip),
[aggregate receipt](../data/experiments/p18-accepted.json),
[coverage addition](../data/experiments/p18-coverage-addition.json) and
[job log](../data/experiments/p18-run-40352704602-job.log.gz) are permanent.
Artifact ID: `12664414093`. ZIP SHA-256:
`feb14989f1335459fb8d4a2b36bec234b3e0560e02ce372fb064e502331030a9`.
After download, ZIP SHA/CRC, source/controller/verifier/ledger/predecessor,
all child/transcript/time hashes, bounds, counts, resource summaries and
byte-identical cumulative addition passed again. The complete arithmetic
replay was performed in the separate hosted Python process; downloaded
intake checks did not repeat the 786 million arithmetic trials.

Source head: `5cb5ef5f254e03936c9547139304c95db628b92c`.
Tested synthetic PR merge: `b2982e5e95f66fa45553f18b3376df3a5cddd5d8`.
Historical full replay checks out that source and uses
`GITHUB_SHA=b2982e5e95f66fa45553f18b3376df3a5cddd5d8 GITHUB_RUN_ID=40352704602`
with `tools/search_discovery_p18.py --verify --output EXTRACTED/p18`.
These environment labels reproduce metadata; actual source hashes and every
arithmetic transcript are checked. This is not a new remote attestation.

Per-cell accepted counts:

| delta | Exact trials | BigZ lookups | Primitive witnesses |
| ---: | ---: | ---: | ---: |
| 17 | 45,814,784 | 54,296 | 0 |
| 18 | 46,342,144 | 91,771 | 0 |
| 19 | 46,845,952 | 33,040 | 0 |
| 20 | 47,329,280 | 119,204 | 0 |
| 21 | 47,793,152 | 128,643 | 0 |
| 22 | 48,239,616 | 32,902 | 0 |
| 23 | 48,670,720 | 56,888 | 0 |
| 24 | 49,086,464 | 115,365 | 0 |
| 25 | 49,488,896 | 205,054 | 0 |
| 26 | 49,878,016 | 74,884 | 0 |
| 27 | 50,255,872 | 44,059 | 0 |
| 28 | 50,623,488 | 62,596 | 0 |
| 29 | 50,980,864 | 128,361 | 0 |
| 30 | 51,326,976 | 85,019 | 0 |
| 31 | 51,664,896 | 81,529 | 0 |
| 32 | 51,993,600 | 26,813 | 0 |

The new [index-p18.json](../data/experiments/index-p18.json) retains every
accepted predecessor and adds exactly sixteen disjoint cells. The current
pointer hashes it; the readable [territory map](../data/experiments/TERRITORY.md)
records **56 high-height cells, 1,716,786,944 trials and 3,823,545 BigZ lookups**.
The full B320 census, calibration scopes, external reports and exact algebra
conformance remain separate categories.

Positive coverage at e=2,760,001 is now delta=1..32,64,256 with a=1..1024.
This does not exhaust a target height. Delta 33..63 and other unlisted gaps,
a>=1025, other high target heights, and general signed orderings remain open.
The independent [pair reconstruction experiment](PAIR_SUM_RECONSTRUCTION.md)
adds algebraic capabilities and mixed benchmark evidence, with zero new
Euler search cells. A production cached-table benchmark is still required.
