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

Status: native comparison pending. This algorithm-development track adds
**zero Euler discovery cells**. Positive gaps 17..32 are being searched
separately using the existing accepted controller, not this new algorithm.
Future work must benchmark the actual cached production workload and
derive complete finite bounds before replacing any discovery path or
admitting general signed Euler boxes.
