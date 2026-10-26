# Exact signed fifth-power pair reconstruction: derivation and experiment

For a remaining Euler pair target `R=e^5-c^5-d^5`, write
`R=a^5+b^5`, `s=a+b`, and `p=a*b`. Expanding the cyclotomic pair norm gives

```text
R = s*(s^4-5*p*s^2+5*p^2)
q = R/s                         (only if s!=0 and s divides R)
Delta = 5*s^4+20*q
      = (5*s^2-10*p)^2
      = (5*(a^2+b^2))^2
p = (5*s^2-sqrt(Delta))/10
T = s^2-4*p = (a-b)^2
a = (s-sqrt(T))/2
b = (s+sqrt(T))/2                (ordered a<=b)
```

The nonnegative square root of Delta is `5*(a^2+b^2)`, explaining why only
the minus branch is needed for p. Every indicated division requires exact
divisibility; every root is an exact integer square test. No floating point,
probabilistic prime test, incomplete factorization, or coprimality assumption
is used. For `R=0`, the complete ordered pair family is `a=-b`; this case
never divides by s. Other targets cannot have s=0.

## Finite completeness argument

For the declared box `-B<=a<=b<=B`, all possible sums lie in `[-2B,2B]`.
Enumerate that entire interval, excluding zero after handling `R=0`.
For each exact divisor s, require the two square tests, the two integer
divisibilities, and the final pair bounds. Then recheck `a^5+b^5=R` using
native BigZ. Every valid pair has its sum enumerated and satisfies the
displayed equations; reconstructed accepted pairs satisfy the final exact
equation and box checks. This is a mathematical coverage argument; there
is no claim of a machine-checked proof of the native loop or square-root code.

The discriminant square root is at most `10*B^2` and the difference root
at most `2B`. Binary search uses BigZ products, so squaring never overflows.
The explicit `B<=16384` intake cap proves that sum squares, p numerators,
and reconstructed machine integers fit signed 64 bits. Fifth powers,
quotients and discriminants use BigZ throughout. The cap is a resource
policy, not a restriction on the underlying algebra.

Seven new Lean theorems in `formal/lean/PairSumReconstruction.lean` prove
the signed pair-sum model, divisor condition, discriminant equations,
product/difference reconstruction equations and zero-sum equivalence.
They do not yet prove the full enumerator's completeness or its native
lowering. The exact identities passed local Lean 4.24.0; hosted acceptance
uses repository-pinned Lean 4.34.1 and the existing axiom audit.

## Independent comparison

`algebra/pair_sum.mojo` implements reconstruction and a separate baseline
that builds sorted signed fifth powers, scans every a and finds b by exact
binary membership. `tests/test_pair_sum_reconstruction.py` uses a third
method: Python fifth-power hash lookup, without reconstruction, for the
accepted pair set. A separate Python `isqrt` reconstruction checks each
native rejection counter and the exact transcript order.

Python tests cover every attainable target from the full signed box
`[-12,12]^2` (313 distinct targets), plus adjacent target controls. The
37-query native corpus contains tiny signed/zero/repeated-root cases and
larger pairs with summands above 1024, including `(-8192,4097)`, where the
negative term's magnitude exceeds the positive term. Mutated targets and
targets beyond Int64 are included. Zero entries are allowed in this
**pair conformance** experiment; an Euler caller must separately impose
nonzero/positivity, ordering, primitive gcd and novelty requirements.

The hosted benchmark compiles once, then runs 106 exact queries across
both methods. Larger cases have three repetitions, with method order
alternating. Each process's stdout and GNU time wall/user/system/RSS are
preserved and source-bound, along with monotonic wall nanoseconds and
separate compiler resources. A fresh Python process replays all queries.
The executable's hash is recorded; its bytes are temporary build output,
not part of the preserved artifact or a remote-worker attestation.

Timing includes process startup and per-query table initialization; the
baseline does not reuse a power table between queries. This is an explicit
one-query workload, not the cached-table production stripe workload. A
faster result here would not establish an Euler search speedup. A slower
result would be preserved as a negative algorithm experiment.

```sh
python tests/test_pair_sum_reconstruction.py --python-only
pixi run --locked verify
pixi run --locked python tests/test_pair_sum_reconstruction.py --output /tmp/pair-sum-new
pixi run --locked python tests/test_pair_sum_reconstruction.py --verify --output /tmp/pair-sum-new
```

This algorithm-development track adds **zero Euler discovery cells**. Positive gaps 17..32 are being searched
separately using the existing accepted controller, not this new algorithm.
Future work must benchmark the actual cached production workload and
derive complete finite bounds before replacing any discovery path or
admitting general signed Euler boxes.


## Accepted comparison and exact worked example

[Native run 40353821388](https://github.com/larsbx/euler-powers-research/actions/runs/40353821388)
passed all 106 queries and fresh full replay at source
`9ba3ccff7b63154578585657b616d5a5c735ef54`, synthetic test merge
`ceed4c4e4808a814b8fcf44c6595c850fbb83b55`. The original 216-file
[ZIP](../data/algebra/pair-sum-40353821388.zip),
[extracted receipt](../data/algebra/pair-sum-40353821388-accepted.json),
[native job log](../data/algebra/pair-sum-40353821388-job.log.gz), and
[formal job log](../data/algebra/pair-sum-formal-40353821271-job.log.gz)
are permanent. ZIP SHA-256:
`2952e72aa9118a8ec6a6c76b2c773a8773b3224381804cc28909793c998a9978`.
Downloaded ZIP CRC, source/resource hashes, all raw transcripts and a
separate local full Python replay passed again. All five source-head
workflows passed, the latest-head review had no findings, and PR #55 merged.
Pinned Lean 4.34.1 built the new proofs and audited 348 theorems with no
nonstandard axioms (including generated proof auxiliaries).

For the seeded signed pair `a=-8192`, `b=4097`, the native algorithm recovered

```text
R = -35,739,158,580,566,142,975
s = -4095
sqrt(Delta) = 419,471,365
p = (5*s^2-sqrt(Delta))/10 = -33,562,624
sqrt(T) = 12,289
a = (s-sqrt(T))/2 = -8192
b = (s+sqrt(T))/2 = 4097
```

This is a pair reconstruction control beyond Int64, not a new Euler
identity. At B=8192, all 32,768 nonzero sums were tested for this target;
72 divided R exactly, one passed the bounded discriminant square test,
and one pair passed the complete reconstruction. Increasing R by one
left four exact divisors and zero square survivors/pairs in the same box.

| B | Target from seeded pair plus offset | Scan median ms | Reconstruction median ms |
| ---: | --- | ---: | ---: |
| 64 | (-64,3), offset 0 | 9.918 | 9.928 |
| 64 | (8,63), offset 1 | 9.657 | 10.228 |
| 4096 | (1025,3183), offset 0 | 15.439 | 13.547 |
| 4096 | (-4096,2049), offset 0 | 16.772 | 17.062 |
| 8192 | (4097,8191), offset 0 | 22.515 | 18.795 |
| 8192 | (-8192,4097), offset 0 | 22.483 | 23.666 |
| 8192 | (-8192,4097), offset 1 | 22.472 | 20.251 |
| 8192 | (8191,8192), offset -1 | 21.629 | 19.716 |

Each median uses three interleaved same-binary process invocations. Across
all 53 invocations per method, process wall sums were 0.722273314 seconds
for scan and 0.677232561 seconds for reconstruction. Maximum query RSS
was 25,612 KiB. Compilation separately took 3.61 seconds, 4.98 user seconds,
0.19 system seconds and 254,024 KiB maximum RSS. The full acceptance process
was 5.56 seconds / 254,024 KiB; fresh replay was 0.29 seconds / 69,228 KiB.
Raw per-query wall/user/system/RSS and nanosecond timings remain in the ZIP.

The mixed case results and startup/table costs do not establish a speedup
for cached Euler stripes. The existing discovery algorithm remains in use.
Historical replay uses the recorded source hashes and
`python tests/test_pair_sum_reconstruction.py --verify --output EXTRACTED/pair-sum`.
