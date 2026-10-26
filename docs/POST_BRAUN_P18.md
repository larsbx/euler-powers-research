# P18: untouched positive cancellation gaps 17..32

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

Status: planned, not yet accepted. Planned cells are not added to the
current ledger. Acceptance would extend restricted positive coverage
through delta=32 at this one height, with `a<=1024`; it would not exhaust
the height or address other target heights, larger a, or general signed cases.
