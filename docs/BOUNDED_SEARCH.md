# Mojo bounded positive Euler fifth-power census

## Mathematics and completeness

For each integer `2 <= e <= B`, the native kernel enumerates every
`1 <= a <= b < e` and computes the exact sum `a^5+b^5`. It sorts the
resulting pair sums. For every `1 <= c <= d < e` it searches for the
complement `e^5-c^5-d^5` by binary search. Every hit is reconstructed
by enumerating all `a <= b <= c`, checking the exact equality and
`gcd(a,b,c,d,e)=1`. Multiple pair representations are not discarded.

**Completeness at a bounded height follows from the loop coverage**, not from
a probabilistic assertion or a modular heuristic. The search covers ordered,
strictly positive, primitive solutions only. It does not cover negative or
zero summands, and it says nothing about E5-1 through E5-5.

A hard guard enforces `B <= 1000`; then any individual fifth power
is at most `10^15`, and every cached pair sum is at most `2*10^15`,
strictly below the `Int64` limit. The proof obligation changes before
the bound can be raised. For unbounded fifth-power verification we use the
shared arbitrary-precision `BigZ` verifier, not this guarded search.

## Finite-ring obstruction profiles

`kernel/residue_sieve.mojo` computes fifth-power residues and every
feasible signed five-term tuple modulo 7, 11, 25 and 31, recording the
number of bases divisible by the designated prime. It exhausts all base
residue classes through a Boolean dynamic program, not numerical
sampling. In particular, modulo 11 and 25 admit only counts 1, 3, 5;
primitive solutions rule out all five divisible entries. The latter
deduction agrees with the elementary proofs in `docs/FOUNDATIONS.md`.

## Commands

On Linux x86-64, with Pixi and Git installed:

```sh
pixi run verify
pixi run verify-research
pixi run census-144
```

The second command runs the Mojo sieve and positive census, plus an
independent Python oracle which implements **hash-indexed** complementary
pair sums instead of Mojo's sorted-array search. The `e<=144` native
output must equal `certificates/census_e144.txt` byte-for-byte after
line splitting. Every certificate is independently checked for
canonical positive coordinates, primitive gcd, strict ordering and the
full integer identity. The oracle then prints a stable domain-separated
SHA-256 digest of the sorted certificate records.

The certificate file is an exact, reproducible **bounded computational
record**, not a general Diophantine theorem. A saved search report should
include the repository commit SHA, pinned `finite-math-kernels` SHA,
Mojo/Pixi versions, height bound, command, complete stdout and digest.

### Scaling safely

The small CI lane is intentionally deterministic and serial. Parallel
work partitioned by target height `e` is possible; a future implementation
must prove coverage of disjoint e-intervals and stable deterministic
aggregation. Do not label a shard-only or checkpointed result exhaustive.
No GPU, distributed runtime, or performance claims are part of this phase.

## Deterministic height sharding

The primary kernel also accepts an **inclusive** height interval:

```sh
pixi run census-shard-a   # CENSUS 2 72 <count>
pixi run census-shard-b   # CENSUS 73 144 <count>
```

Each invocation covers every positive, ordered, primitive solution whose
target `e` is in that interval. Different intervals are independent and
can run in parallel processes; `verify-research` exercises that execution
with two workers, checks closed-interval partition coverage, independently
recomputes each shard, and compares the union against the full unsharded
census. Nothing assumes cross-shard shared memory or a single process,
and duplicate height ownership is rejected by the independent test.

For the verified default fixture through height 144, exactly one
primitive positive tuple occurs: `27 84 110 133 144`. The domain-separated
certificate SHA-256 for this fixture is
`7956676fa8d1210a838240119f4b7f306d13f3fe4deaea6770bb8aac62ea16f9`.
An independent digest makes the record portable, not a proof of unbounded
completeness.
