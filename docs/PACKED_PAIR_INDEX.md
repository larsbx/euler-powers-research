# P3: collision-preserving packed pair index and native benchmarks

**Domain:** strictly positive primitive fifth-power search, ordered
`1 <= a <= b <= c <= d < e <= B`, with `2 <= B <= 144` and
`1 <= M <= 35`. No signed or zero-term results are implied.

## Concrete algorithm

For each target height `e`, enumerate every ordered left pair
`1<=a<=b<e`. With exact sum `s=a^5+b^5`, store the **representation**
(not merely `s`) as

`P(s,a,b) = (145*s + a)*145 + b`

in a sorted residue bucket indexed by `s mod M`. The radix is fixed at
145 for the whole bounded program, and both digits satisfy
`1<=a<=b<e<=144<145`. It is consequently impossible for different
pairs with the same sum to overwrite each other or cause radix carries.

For each right pair `c<=d<e`, calculate the signed Int64 complement
`t=e^5-c^5-d^5`. Discard `t<=0`; count every strictly positive right
visit under its unique canonical unordered residue pair; lower-bound
the matching left bucket at `145^2*t` and scan until the quotient
`P/145^2` changes. Decode `a=(P%145^2)/145`,
`b=P%145`. Accept an exact representation only if `b<=c` and
`gcd(a,b,c,d,e)=1`. Different representations yielding the same fifth
power sum are all inspected. This replaces the former `O(c^2)`
exhaustive reconstruction *per prefilter hit* with a
`O(log K + R)` range query for bucket length `K` and matching
representation count `R` (plus native allocation and indexing costs).

The output remains the existing `E5PARTv1` records; per-key SHA-256
commitments from independent replay remain `E5PART-REPLAY-v2`.
Neither the modulus nor the index imposes an additional mathematical
restriction on the target equation.

## Mathematical and machine envelope

Since `s <= 2*144^5 = 123834728448`,
`0 <= P <= (2*144^5*145+143)*145+143 =
2603625165640078 < 2^63`. Every packed intermediate is nonnegative
and at most `P`. Lower-bound keys `145^2*t` for
`0<t<=144^5` are smaller. All pair powers, right sums and
signed complements fit Int64. The guard `B<=144` must not be widened
without revisiting these digit, modulus and overflow proofs.
At `e=144` the live index holds `144*143/2 = 10,296`
packed `Int64` records, i.e. 82,368 bytes of scalar payload. The
two `M^2` `Int` counters require up to 19,600 bytes of 64-bit scalar
payload for `M<=35`. Allocator overhead, resident code, caches and
compiled-runtime memory are not included in these theoretical payloads.

`formal/lean/PackedPairIndex.lean` proves injective decoding, the
contiguous range of records for a fixed exact sum, and the conservative
Int64 upper bound for the mathematical encoding. Its theorems are
kernel-checked via the default Lake build and axiom audit. They do
not prove a particular compiled Mojo `sort`, `lower_bound`, or
array indexing operation correct. Existing native lower-bound
observational conformance and independent exact arithmetic oracle
remain part of the gate.

## Native conformance

The production module provides `build_indexed_buckets` and
`matching_indexed_pairs`. The shared helper probe checks executed
Mojo against independently enumerated Python tuples for: distinct
collisions such as `(1,4),(2,3)` at synthetic target 5; three
same-sum representations `(1,1),(1,2),(2,2)` from equal synthetic
powers; the canonical ordering restriction `b<=c`; and moduli
`1,2,7,11,35`. Synthetic powers are not fifth-power certificates.
The nonempty positive `B=144,M=35` acceptance case must retain
2,574 partition rows, 475,063 right-pair visits, and the sole
primitive positive witness `(27,84,110,133,144)`. Replay checks the
same previously committed digest root.

## Performance evidence and reproducibility

`tests/benchmark_pair_index.py` retrieves the exact archived
**merged P2 implementation** at commit
`792e0e9ca70575c41202c81e47bd23a8dfc8d571` using local Git
history, compiles the P2 source and current candidate using **the
same pinned Mojo toolchain and dependency**, and executes both for
`B=48` and `B=144`, each with `M=35`, three repetitions apiece.
Execution order alternates across repetitions. Every result stream
is independently compared to the exact Python oracle and to the
preexisting per-partition root at `B=144` before recording metrics.

The CI job (full-history checkout) records GNU `time` wall seconds and
peak Linux RSS KiB for each execution, plus native per-partition
positive-complement visit counts, platform, current Git commit,
source SHA-256 and Mojo version. It preserves a JSON run artifact
named `native-pair-index-benchmark` for inspection. No arbitrary
performance threshold gates correctness, and CI timings do not prove
a cross-machine or asymptotic speedup. The reported visit count
excludes right pairs with nonpositive complements and is taken from
actual native partition records, not a theoretical loop-count estimate.

Run in the pinned Linux/Pixi environment after fetching Git history:

```sh
pixi run --locked verify-research
pixi run --locked python tests/benchmark_pair_index.py \
  --output benchmarks/results/native-comparison.json
bash tools/verify-formal.sh
```

This remains a finite positive-domain search and not an independent
reproduction of Braun's million-height searches. No new positive
solution or resolution of E5-1 through E5-5 is implied.
