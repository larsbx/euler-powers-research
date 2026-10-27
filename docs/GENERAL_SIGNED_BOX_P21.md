# P21: complete signed pair/triple discovery experiment

The objective remains a genuinely new nontrivial primitive fifth-power class,
positive or signed. P21 is a finite discovery experiment; a negative result
and implementation acceptance do not satisfy that objective.

## Finite domains and discovery rationale

For a finite increasing set S of positive integers, enumerate every nonzero
five-term zero sum with all absolute bases in S, modulo permutation and global
sign. Repeated bases are allowed; no pairwise coprimality is assumed.

The production plan is fixed in `tools/search_signed_box.py`:

* S = {1,...,1024}: complete signed box, including both 1=4 and 2=3 partitions.
* S = {1,...,256} union {3,000,001,...,3,000,256}: mixed small/large magnitudes,
  beyond the largest known primitive target in the registry. This searches
  unrestricted sign assignments in this set without fixing a target, gap,
  smallest summand or ordering between positive and negative magnitudes.

The dense box supplies a complete signed baseline, rather than another
fixed-height grid; it also recovers the 1966 identity and its admitted scalings.
The mixed domain tests a different algebraic cancellation structure: two large
terms can occur on each side with a remaining small term. These finite sets
are a tractable first experiment, not a claim that a new class is likely here,
or that these bounds improve author-reported literature searches. No new
coverage is claimed for replays or the strategy-comparison corpus.

## Completeness argument

Sort any admissible five bases. Their median is nonzero. If it is negative,
negate all bases and reverse their order. Thus exactly one of the two global
orientations has the ordered form a<=b<=c<=d<=e with c>0. The equation becomes

    a^5+b^5 = -(c^5+d^5+e^5).

The right side is strictly negative. Odd fifth powers are strictly increasing,
so a^5+b^5<0 is equivalent to a+b<0. For each negative base a=-S[u], all eligible
ordered pairs have b from a through the positive base immediately below -a,
excluding zero. The native index uses signed ranks, so this statement also
holds in the noncontiguous domain. There are exactly N^2 pair representations
(sum of 2u-1 for u=1..N), retained even when sums collide.

For each positive rank c=1..N, native loops enumerate every c<=d<=e<=N once.
The row has (N-c+1)(N-c+2)/2 targets, giving N(N+1)(N+2)/6 targets overall.
The exact sorted pair index returns every matching representation with b<=c.
Consequently every sorted oriented identity in the declared domain is visited
once, before primitive/equivalence reduction. Opposite-term cancellations and
zero bases are excluded. Primitive reduction and equivalence classification
are performed by the accepted PR #59 intake, with a separate native BigZ
verification of cleared and primitive terms.

`SignedBox.lean` proves the pair/triple equation, global sign equivalence,
reversal of sorted order, nonzero-median orientation and positive-tail
implications. These are reductions, not a formal verification of native
loops, arbitrary-precision arithmetic, memory allocation or the compiler.

## Choosing the computational strategy

The exact divisor/two-square reconstruction from PR #55 is exposed as a
collection API; its existing printed interface and counters are preserved.
Both methods receive exactly the same complete triple-target streams at
bounds 16, 24 and 32, three repetitions in alternating order. Processes use
the same precompiled binary. Index construction is included in every indexed
measurement; compilation is measured separately.

The indexed strategy has O(N^2) stored records and O(N^3 log N) target work.
Full bounded reconstruction tries 4B nonzero pair sums per target, giving
O(B^4) divisor trials in the dense box and expensive exact division/squares.
No complete factorization oracle is available. The driver requires measured
median indexed wall time below reconstruction before starting production.
Timing is workload-specific; no universal speed claim is made.

## Execution, receipts and independent replay

Production is partitioned into consecutive positive-median rank intervals of
width 128. Every shard rebuilds the index; there is no cache or hidden search
state. A shard prints its exact domain, each nontrivial hit, every median-row
count and BigZ sum of all target values, and a final completion record.

Each child has a 32-GiB virtual-address limit (tcmalloc reserves large virtual
ranges), 240 CPU seconds, 300 wall seconds and a 4-MiB output-file limit.
Per-child `wait4` peak physical RSS is recorded and admission rejects values
above 768 MiB for search or 2 GiB for compilation. This RSS check is after
execution, not a kernel-enforced 768-MiB physical limit. Hosted execution
additionally uses the existing `run_research_cgroup.sh` whole-process-tree
2-GiB physical-memory/no-swap/1200-second cap, including Python replay.
Timeouts, failures, missing rows, gaps, overlaps and mismatches receive no
coverage credit; no accepted receipt is written until every required stage
succeeds and all native streams agree with independent replay.

Python builds a separate arbitrary-precision hash index from all ordered
signed pairs, selects by exact sum sign, then independently enumerates every
triple and compares all raw native rows and hits byte for byte. It never uses
native hits to choose which targets to check. Original stdout, stderr,
per-child resources, binary digest, source hashes, dependency pin, workflow
run and commit identifiers are retained. A second fresh replay checks the
saved streams. Checksums aid inspection; independent full traversal and
source inspection support coverage, rather than checksums alone.

Run after initializing the pinned arithmetic dependency:

    pixi run --locked python tests/test_signed_box.py
    pixi run --locked python tools/search_signed_box.py --output benchmarks/results/p21
    pixi run --locked python tools/search_signed_box.py --verify --output benchmarks/results/p21

Known classes, scaling duplicates and raw hits remain separate. Absence from
the registry yields only `candidate_requires_current_literature_review`.
Any such candidate requires current primary-literature/equivalence review
before novelty can be claimed. Finite negative results do not imply global
nonexistence. P21 target counts must not be added to the differently defined
P19/P20 trial units; some calibration territory can overlap earlier work.
