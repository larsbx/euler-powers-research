# P7 — Structured BigZ pairs, exact sorting, and bounded height shards

## What is actually implemented

A new **Mojo-native** pair-index module is
`kernel/bigz_pair_index.mojo`. Each record has three independent
fields:

```mojo
struct BigPair(Copyable):
    var sum: BigZ
    var a: Int
    var b: Int
```

The `sum` is an arbitrary-precision shared
`finite_exact.bigint_z.BigZ` value; no radix encoding, integer
narrowing or floating-point conversion takes place. A stable
bottom-up mergesort orders records lexicographically by the exact
sum, then `a`, then `b`. A binary lower bound on the exact BigZ
sum finds the first representation, and the matching iterator
preserves all distinct pairs with the same fifth-power sum. The
synthetic probe exercises several same-sum representations at
`2^63`, plus negative and larger positive keys, to verify the
representation is not silently limited by signed Int64.

The `kernel/bigz_shard.mojo` driver independently runs a bounded
positive E5 census for an explicitly declared height shard:

```sh
pixi run --locked mojo run -I kernel -I .deps/finite-math-kernels/kernel \
  kernel/bigz_shard.mojo 319 320 35
```

Accepted parameters satisfy **2 <= START_E <= END_E <= 320**,
at most **four target heights** in one call, and **2 <= M <= 35**.
These are deliberate resource policies, *not arithmetic limits of
BigZ*. M=1 remains available in the existing packed search, not
this ring-backed BigZ shard. Every target height constructs its own
complete `1<=a<=b<e` BigZ pair index, enumerates every
`1<=c<=d<e`, computes the signed complement in BigZ, and uses
the pinned shared exact `Z/99000Z` prefix filter as a sound
necessary condition before exact pair lookup. Primitive matches
are checked against both the exact complement and GCD, and
emitted as the established `CERT E5v1` witness.

A stream is explicitly scoped by

`DOMAIN E5BIGSHARDv1 START END M`

and closed by `SHARD START END M VISITS CERTIFICATES`.
The interior `PART` rows preserve the E5PART counting/ownership
convention. The new **shard** header deliberately distinguishes
a subset of heights from a complete B2..B320 census: it must not
be used as an unqualified complete-search certificate.

## Proof and independent testing

The separate `formal/lean/BigPairIndex.lean` module gives a
mathematical, radix-free record order, proves sorting preserves
each enumerated left-pair record and that equal structured records
have equal sum/index coordinates, and shows every valid positive
E5 solution has its corresponding exact left record. The
compiled Mojo sorting and binary search are tested by adversarial
finite input probes; these source-level Lean theorems are not
proofs about the compiler binary.

`tests/test_bigz_shards.py` compares **actual native stdout**
with an independently implemented exact Python multimap oracle for
four bounded shards:

- e=2..5, M=7 (small baseline).
- e=143..144, M=35 (historical nonempty positive witness).
- e=255..257, M=35 (old radix range crossed).
- e=319..320, M=35 (new bounded heights).

The test also rejects invalid bounds, zero/modulus-1 ring
parameters and noncanonical decimal arguments. It checks every
candidate visit, every PART count and every ordered witness, not
only a digest. The signed known-solution program, the B144 and
B256 packed streams, and the independent replay digest commitments
are still required unchanged by their existing CI gates.

## Limits and further work

This implements a **lossless arbitrary-precision index** and finite
positive height shards but **does not** establish a complete search
for all heights through 320 or beyond. A later milestone must add a
monotonic, gap-free shard plan and independent replay of complete
height coverage, including completion/abort receipts, and suitable
memory/time limits for the larger ranges. Production-scale testing
should use a bounded fixed workload before extrapolating
performance; multilimbed BigZ sorting is expected to be more
expensive than checked packed Int64 on small values.

The immutable `finite-math-kernels` pin, exact arithmetic, formal
source obligations and witness-certificate trust boundary remain
unchanged. No additional positive solution or reproduction of any
large published exhaustive search is claimed.
