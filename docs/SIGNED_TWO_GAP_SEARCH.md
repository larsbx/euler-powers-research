# Signed two-gap search outside the old magnitude ordering

The discovery goal is a genuinely new nontrivial primitive class, positive
or signed. This experiment searches an expressly signed structural region
the existing near-cancellation controller cannot reach: the negative
summand has magnitude `u>b`. It does not repeat the accepted P14–P19 grid.

## Exact parameterization and complete finite inversion

Write `-u^5+b^5+c^5+d^5=e^5`, with `1<=b<=c<=d<e`, `b<u<e`,
`delta=e-d>0`, `h=abs(c-u)>0`, and `D=e^5-d^5`. There are two orientations:

| orientation | paired terms | equation | full integer r interval |
|---|---|---|---|
| 0 | u=r, c=r+h | D-b^5=F(r,h) | b+1 through d-h |
| 1 | c=r, u=r+h | b^5-D=F(r,h) | b through min(d,e-1-h) |

Here `F(r,h)=(r+h)^5-r^5`. An empty interval has no admissible pair.
For positive integer r,h, its successor difference is

```
h*(20*r^3+(30*h+30)*r^2+(20*h^2+30*h+20)*r
   +5*h^3+10*h^2+10*h+5) > 0.
```

Thus for each declared `(e,delta,h,b,orientation)` there is at most one r.
Native Mojo checks it by exact BigZ lower-bound binary search over the full
interval, without enumerating millions of c values or assuming small u.
All exact hits are rechecked against the original fifth-power identity and
five-way gcd. No candidate is a discovery until independent arithmetic,
canonical equivalence and current primary-source novelty review pass.

Before expensive inversion, necessary modular images of F are built from
**every residue** modulo 99000, 41 and 61. These are complete polynomial
images over full periods; rejecting an absent image is sound. Separate
images do not assert a sufficient CRT condition or an expected rejection
probability. Exact interval inversion remains authoritative.

The independent Python replay uses a different algorithm on **every trial
before modular gates**. Since h>0, a solution requires h to divide q=F(r,h),
and

```
16*(q/h)+4*h^4 = 5*((2*r+h)^2+h^2)^2.
```

Check divisibility by 5, take an exact integer square root, subtract h^2,
take another exact square root, check parity, then recover r. Finally check
the original exact fifth-power difference and interval. Every possible pair
must follow these steps, and any reconstructed pair is checked directly.
This replay also detects a modular gate rejecting a real pair. No rounded
roots, integer factorization oracle or floating-point powers are used.

Five Lean theorems establish the polynomial identities/rearrangement in
`formal/lean/TwoGap.lean`. The formal build/axiom audit must pass before
acceptance; these identities do not formalize the full native enumerator,
integer square root implementation or compiler.

## First declared batch

| parameter | values |
|---|---|
| e | 1956877, 1956878, 1956879, 2760001, 3000001 |
| delta | 64, 665, 4096, 16384 |
| h | 64, 1024, 9010, 16384 |
| b | 65537..131072 and 524289..589824 |
| orientation | both |
| r | every admissible value through complete inversion above |

These are 160 declared parameter cells (320 oriented cells) and 20,971,520
exact b/orientation trials. The heights include neighbors of Braun and
heights beyond the earlier single-height emphasis. Both positive b bands
exceed the prior small-summand ranges; the gaps extend well beyond 256.
No b value between these bands is implicitly covered. The parameter sets
are selected finite samples, not complete intervals of heights or gaps.

This experiment excludes u=b, u=c, u>=e, two negative input summands,
undeclared b ranges and every undeclared e/delta/h. It is not exhaustive at
any full height. The coverage unit differs from the old `(c,abs(a))` loops:
do not add these trial totals to the P19 ledger's arithmetic count.

Calibration separately searches Braun at `e=1956878,delta=665,h=9010`,
`b=719114..719116`. It must find exactly the known Braun identity at b=719115;
this is not new territory or discovery credit. Small Python pair/neighbor
tests are algebra controls, also with zero discovery credit.

## Reproduce, certify and measure

```
pixi run --locked verify
pixi run --locked python tests/test_two_gap.py
bash scripts/run_research_cgroup.sh /usr/bin/time -v -o two-gap-time.txt \
  pixi run --locked python tools/search_two_gap.py --output fresh-two-gap
bash scripts/run_research_cgroup.sh /usr/bin/time -v -o replay-time.txt \
  pixi run --locked python tools/search_two_gap.py --replay fresh-two-gap
```

The controller compiles once and uses a clean immutable arithmetic checkout.
Per-cell GNU time records give wall/user/system time and maximum RSS;
process nanoseconds include invocation overhead. Outer GNU time includes
compilation, controller and initial replay, with fresh replay timed separately.
Hosted physical cgroup limits are 2 GiB RAM, no swap, 1200 seconds per phase;
each native cell has a 60-second timeout. These are resource policies.

The original stdout, per-cell time reports, calibration, any candidate
admissions, exact plan, source hashes, dependency pin, workflow source/run
labels and predecessor P19 ledger hash are preserved. A receipt is written
only after all native outputs match the independent exact Python oracle.
The separate replay checks the entire finite plan again. A GitHub source
label alone is not proof of execution; preserve original hosted artifacts
and job logs alongside the source-bound records before accepted publication.

Current status: Python pilot and small algebra controls have passed;
native execution, formal validation and accepted evidence publication remain
pending. No new identity or accepted native search coverage is claimed here.
