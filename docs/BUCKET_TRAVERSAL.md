# P2: one-pass bounded pair-sum bucket traversal and independent replay

**Status:** implemented and subject to the pinned hosted CI gates (PR against main).
This is a *strictly positive*, primitive, ordered fifth-power **finite census**
algorithm, not an exhaustive verification of any published million-height search.

## Executable traversal

`kernel/pair_partition.mojo` retains the P1 `E5PARTv1` wire records but
changes candidate processing: each height `e` constructs **all**
`1 <= a <= b < e` fifth-power sums in sorted per-residue buckets. It
then traverses each `1 <= c <= d < e` right pair **once**, computes the
exact signed complement `e^5 - c^5 - d^5`, and routes strictly
positive targets directly to their unique key

`(min(target % M, right % M), max(target % M, right % M))`.

A sorted bucket membership test is only a *prefilter*. Every candidate
`a <= b <= c` is reconstructed before exact identity and GCD acceptance;
colliding sums never overwrite each other's representations.
Per-key visit and hit counters are accumulated in two dense `M × M`
arrays, and `PART` rows (including empty partitions) are printed in
canonical order. `CERT` records can precede their `PART` row; replay
does not rely on certificate placement.

The previous algorithm visited right pairs once **per compatible key**.
The new algorithm visits them once **per height**. This removes that
redundant outer traversal; it does **not** prove an elapsed-time speedup
because bucket building, membership, and reconstruction still cost time.

## Bounded machine and memory contract

The unchanged executable intake is `2 <= B <= 144`,
`1 <= M <= 35`; a malformed/noncanonical invocation is rejected.
For each height there are exactly `e(e-1)/2` left-pair records and
`e(e-1)/2` enumerated right pairs. The maximum per-height bucket
payload contains 10,296 `Int64` sums (82,368 value bytes); the two dense
counter vectors have at most 2,450 integer entries (19,600 value bytes
on a 64-bit machine), plus 145 cached `Int64` powers at the maximum
bound. Each residue list and temporary reconstruction list adds allocator,
header and tuple overhead not included in these payload figures.
The asymptotic live storage is `O(e²+M²+B)`; no measured peak RSS
figure is asserted.

All fifth powers are <= `144^5 = 61,917,364,224`,
left/right sums <= `2·144^5`, and signed complements lie within
`[-2·144^5,144^5]`. These conservative bounds fit signed Int64
without overflow. Modulo is applied only to nonnegative sums or
strictly positive complements; there is no negative-remainder ambiguity.
The underlying `positive_census.mojo` has a separately proved
`B<=1000` machine envelope; **that wider bound does not apply
to this partition executable**.

## Independent execution evidence and replay

`tests/replay_partition.py` accepts raw Mojo stdout with an expected
height, modulus, independent Python pair-hash oracle and optional pinned
digest root. It checks exact header/footer, canonical ASCII integer
tokens, full ordered key set (including zero-hit keys), visits, count
accounting, witness identity, ordering, primitivity, duplicate rejection
and oracle equality. It domain-separates every partition leaf using
`E5PART-LEAF-v2`; its root commits in key order to every leaf with
`E5PART-ROOT-v2`. The `digest_lines` function emits one
`PARTDIGEST e lo hi SHA256` per key followed by `ROOTDIGEST SHA256`.
No hashing code is taken from Mojo. This preserves the v1 native
producer format while adding a *versioned verification artifact*.

Pinned domain `B=144, M=35`:
- 2,574 canonical partitions, 475,063 positive-complement right visits.
- One primitive certificate: `(27,84,110,133,144)`.
- Independent replay root:
  `5b8ed68d8512bb11bf4ac57e2f79657e65893427c157c0615b784d86671af482`.

Run the exact pinned checks:

```sh
pixi run --locked verify-research
pixi run --locked pair-partition > /tmp/e5part.txt
pixi run --locked python tests/replay_partition.py /tmp/e5part.txt 144 35 \
  --expected-root 5b8ed68d8512bb11bf4ac57e2f79657e65893427c157c0615b784d86671af482
bash tools/verify-formal.sh
```

The CI regression injects wrong domains, duplicate/missing keys,
noncanonical integers, falsified counts, an omitted certificate and
a wrong root. A stale artifact **from a different declared height or
modulus** is rejected. An identical valid stream replayed at the same
domain remains indistinguishable from a fresh run: SHA-256 is an
integrity commitment, **not a freshness or authenticity signature**.
Preventing malicious same-domain replay requires a separately specified
challenge, signer or trusted-run attestation protocol.

## Proof and authority boundary

`PairTraversal.lean` proves that each valid ordered positive primitive
tuple has a right pair in `orderedPairs`, its left pair occurs in the
corresponding residue bucket, and right routing selects exactly one key.
It reuses P1's source-level bucket multiplicity and key compatibility
lemmas, including noninjective moduli and equal residues. These are
kernel-checked **Lean mathematics**, not a universal compiled-Mojo
refinement. The independently executed Python oracle and comparison to
the unpartitioned Mojo census remain essential finite-conformance
evidence, and cannot prove search completeness for an unbounded height.

The Quint shard/publish model is unchanged: this PR changes search
traversal and read-only evidence replay, not worker admission, retry,
financial authority or publication transitions. Neither a new positive
solution nor a resolution of E5-1 through E5-5 is claimed.

## Further P2 obligations

Before expanding `B` or claiming production-scale acceleration:
provide measured pinned-toolchain elapsed time, peak RSS and iteration
counts on **the same bounded domains**; replace repeated exhaustive
`matching_pairs` reconstruction with a representation-preserving
index; consider a Lean-executable oracle of the actual traversal; and
add signed/nonnegative models only as separately scoped programs.
