# Verified small-domain pair-sum residue partitions

Issue #25 implements the algorithmic contract motivated by Braun v4, §4.3
and §4.5. It does not reproduce the author's large exhaustive searches.

## Domain and ownership

The Mojo prototype accepts canonical decimal `2 <= B <= 144` and
`1 <= M <= 35`. Its census is exactly the existing strictly positive,
ordered primitive program:

`1 <= a <= b <= c <= d < e <= B`, `gcd(a,b,c,d,e)=1`,
`a^5+b^5+c^5+d^5=e^5`.

Set `s=a^5+b^5`, `t=c^5+d^5`. The owning key is
`(min(s mod M,t mod M), max(s mod M,t mod M))`.
These are residues of **pair sums**, not of individual bases.
For each height, enumerate all `0 <= lo <= hi < M` with
`(lo+hi) mod M=e^5 mod M`. Every exact identity has one such key;
exchanging its pair sums preserves that key. This also works for equal
residues and `M=1`.

`PairPartition.lean` proves compatibility, unique ownership, list-partition
coverage and non-overlap, and preservation of record multiplicities. It
also links compatibility to the existing `Valid` E5 predicate. The module
is a default Lake target and is imported into the existing axiom audit.
These are kernel-checked source-level theorems over natural numbers;
compiler correctness and universal refinement of Mojo are not proved.

## Executable construction and collision handling

`kernel/pair_partition.mojo` builds sorted residue buckets containing every
pair sum for `1 <= a <= b < e`, including repeats. Each compatible key
visits right pairs `c<=d<e` whose positive complement belongs to that key.
It binary-searches the complement's residue bucket, then reconstructs
**all** pairs `a<=b<=c` matching the exact complement. Primitivity is
checked only after reconstruction. A sorted multiset is never replaced
by one representative per value or residue.

The bound gives powers at most `144^5`; even `2*144^5` is below `2^63`.
Subtractions use signed Int64 and reject nonpositive complements.
The shared existing `fifth_int`, `primitive` and `contains_sorted` helpers
are reused; the shared finite-math dependency and Mojo toolchain remain
pinned. This small prototype iterates compatible keys and scans right
pairs, so it is an ownership reference, not a claimed speed improvement.
It introduces no distributed worker or admission-state changes; Quint's
operational models remain unchanged and are rerun by the formal gate.

## Independent checks and deterministic evidence

Run:

```sh
pixi run --locked verify-research
pixi run --locked pair-partition
bash tools/verify-formal.sh
```

The independent Python oracle uses an exact-integer hash multimap of all
pair representations and assigns each right pair directly to its key.
It compares all output row multiplicities, visits, certificates and keys.
The partition union must also equal the existing unpartitioned Mojo
census at each identical tested height bound. Cases cover `(B,M)` equal
to `(2,7)`, `(8,1)`, `(8,2)`, `(8,7)`, `(8,11)`, `(8,35)` and `(144,35)`.

A shared-helper Mojo probe checks 25,205 sum-pair keys against Python and
uses deliberately colliding synthetic values to check bucket and
reconstruction multiplicity. Synthetic values are helper tests only,
never emitted as fifth-power certificates. Ten invalid invocations and
seven corrupted output streams must be rejected, including deletion or
duplication of the nonempty certificate, a missing empty partition,
noncanonical integers and inconsistent totals.

The Python test independently checks the primality and distinctness of
factors of 7 and 35, `gcd(5,p-1)=1`, and exhaustive fifth-power injectivity
modulo each factor and each concrete modulus. This is finite verification
for those moduli, not a general number-theoretic proof. Partition coverage
does not assume injectivity; the tested modulus 11 is noninjective.

`certificates/pair_partition_e144_m35.json` records all canonical partition
rows and the domain-separated SHA-256 digest of the sorted ASCII output
stream, plus the existing canonical certificate digest. The fixture is
regenerated only with `pixi run --locked python tests/test_pair_partition.py
--write`; ordinary CI compares it without writing.

For `B=144,M=35`, the verified output has:

- 2,574 partition rows, including zero-certificate partitions.
- 475,063 right-pair visits with strictly positive complements.
- Exactly one primitive certificate: `(27,84,110,133,144)`.
- Certificate SHA-256:
  `7956676fa8d1210a838240119f4b7f306d13f3fe4deaea6770bb8aac62ea16f9`.

Counts describe emitted visits, not all loop iterations. No memory or
runtime benchmark is claimed. Signed bases and zero summands are outside
this program; Braun's distinct signed and nonnegative search limits remain
externally reported claims. Conjectures E5-1 through E5-5 remain open.

## Next implementation boundary

A larger search requires an actual bucket traversal with bounded memory,
a formal connection between its executable candidate traversal and this
partition contract, and independently replayable per-partition evidence.
Changing worker admission or publication semantics would then require a
separate Quint extension. Current bounded agreement does not establish
large-domain exhaustion, a new solution, or an asymptotic conjecture.

## P2 one-pass traversal follow-up

The subsequent [bucket traversal and digest replay](BUCKET_TRAVERSAL.md)
removes the P1 repeated right-pair scan per compatible key while preserving
this exact bounded output format and independently checked partition counts.
