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

**Planned. No P16 negative result or discovery is claimed before the actual
native run, fresh full replay and review pass.** Runtime, memory, exact rejection
counts and per-cell coverage will be recorded from accepted hosted evidence.

Unsearched outside accepted scopes: unlisted delta values, larger first summands,
other high target heights, and general signed orderings (including abs(a)>b).
Even successful completion of this experiment would not be a complete height
census. A candidate needs exact identity, five-way gcd, equivalence comparison
against the known registry and fresh literature review before a discovery claim.
