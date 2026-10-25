# P6: B256 exact positive search with checked wide packed pairs

## Scope and compatibility

The positive ordered primitive fifth-power search remains

`a^5+b^5+c^5+d^5=e^5`, with
`1<=a<=b<=c<=d<e<=B`, and `M` in `1..35`.

Its **supported packed partition domain is now 2<=B<=256**,
extended from 144 without widening the unpartitioned B<=1000
integer census or changing the signed known-example verifier.

The production pair representation is selected from two fixed,
machine-checked encodings:

| Accepted B | Radix | Reason |
|---|---:|---|
| 2..144 | 145 | Preserves historical P1–P5 packing, tests and original B144 SHA digest. |
| 145..256 | 257 | Each pair index digit is <257, and the entire packed value fits Int64. |

The new radix **is not a change to mathematical candidate ordering**,
just the internal lossless representation of `(sum,a,b)`. Existing
`E5PARTv1` records for B144 remain exactly identical to the pinned
manifest. Boundary B145 deliberately selects the wider encoding
and receives a full independent oracle comparison.

## Exact machine range

At B=256, every power satisfies

`0 <= x^5 <= 256^5 = 1,099,511,627,776`,

and pair sums satisfy

`0 <= x^5+y^5 <= 2*256^5 = 2,199,023,255,552`.

Every nonnegative packed value, including each intermediate checked
multiply/add, satisfies

`P(sum,a,b) = (257*sum+a)*257+b`

and is conservatively bounded above by

`145,243,287,006,020,096 < 2^63`.

Signed complements `e^5-c^5-d^5` are between
`-2*256^5` and `256^5`, safely within Int64.
All packed operations use `finite-math-kernels`' checked arithmetic.
A B257 invocation is **rejected before execution**, not silently
narrowed or reported as a complete census.

`WidePackedIndex.lean` proves full base-257 digit decoding, pair
injectivity (including different pairs with the same fifth-power
sum), contiguous exact-sum intervals for binary search, and a
conservative Int64 bound. These mathematical theorems are included
in the default Lake build and existing axiom audit. They are
**not** claims of full Mojo compiler verification.

The P5 exact `m=99000` CRT prefix filter remains in the hot loop
and can only remove candidates that fail the necessary left-pair
residue condition. It does not alter canonical positive-complement
visit accounting or certificate semantics.

## B256 independently replayed native evidence

`tests/test_extended_bound.py` compiles and runs the **real** pinned
Mojo search at B145 and B256, M35. It compares every canonical PART and
CERT record against the independent Python hash-of-exact-integers
candidate oracle, then replays actual native stdout through
`E5PART-REPLAY-v2` and checks the pinned SHA256 root at B256.

| Metric | B144 (historical) | B256 (extended) |
| --- | ---: | ---: |
| Complete canonical partitions | 2,574 | **4,590** |
| Positive-complement right-pair visits | 475,063 | **2,664,481** |
| Primitive positive witnesses | 1 | **1** |
| Witness | (27,84,110,133,144) | (27,84,110,133,144) |

New independent domain-specific B256 replay root:

`157fdbc83048ddc782d8aa04c9691d0c34dabfaf96819a6976dd6671e284e07e`.

The historical B144 root remains:

`5b8ed68d8512bb11bf4ac57e2f79657e65893427c157c0615b784d86671af482`.

These are finite-domain reproducible computational claims, and the
library proofs cover mathematical representation invariants. Neither
source-level proofs nor transcript hashes alone prove an arbitrary
compiled enumeration is exhaustive. Compiled/independent correspondence
is supported by the full finite oracle comparison.

## Execution and follow-up

```sh
pixi run --locked verify-research
pixi run --locked python tests/test_extended_bound.py
bash tools/verify-formal.sh
```

Future expansion beyond 256 should **not** merely increase the radix.
Use an exact `(Int64Sum,a,b)` sorted record where possible, and a
structured `(BigZSum,a,b)` index for values outside checked Int64.
Avoid BigZ-to-Int64 narrowing and introduce a separately tested
ordering and lower-bound proof for multi-limb sums. Keep the
compressed machine-word representation as an optional fast path.
Beyond-bound coverage and the reported large historical searches
remain explicitly unverified by this repository.
