# Formal verification contract: Lean and Quint

**Authority boundary:** Lean 4 is the proof checker for exact arithmetic
specifications and shard partition theorems. Quint 0.33.0 specifies the
bounded-census *workflow*; Apalache checks its safety invariant for a
fixed finite number of transitions. Mojo remains the authoritative
native enumerator of *observed* certificates, and Python the separate
execution oracle. A Quint pass alone is not proof that the Mojo search
algorithm enumerated all positive tuples, nor proof of E5-1–E5-5.

## Lean: mathematical statements (formal/lean/EulerPowers.lean)

- A primitive positive ordered 5-tuple satisfies an exact sum-of-fifth-powers
  identity, strict target bound, and gcd=1. `check_sound` and
  `check_complete` prove a decidable certificate predicate matches its
  mathematical definition.
- `pair_complement_iff` states exactly why meeting in the middle may
  subtract two fifth powers without losing a candidate. The inequality
  side condition is essential for `Nat` subtraction.
- `shards_cover` and `shards_disjoint` prove [2,72] and [73,144]
  partition exactly [2,144] without gaps or overlap.
- `landerParkin_valid` checks the first fifth-power counterexample
  using the Lean kernel; mutated targets and scaled nonprimitive
  candidates are explicitly refused.
- `Audit.lean` checks for nonstandard axioms and expects a minimum
  number of actual theorems. `sorry`/opaque proof holes are not allowed.

The Lean proofs establish facts **about their definitions**, not automatic
refinement of the Mojo implementation. A future deeper refinement step
should prove a precise relation between its loop semantics and the
mathematical enumeration predicate (or verify machine-generated
coverage certificates with a Lean-certified checker). No such claim
is made here.

## Quint: two-shard certification state machine

`formal/quint/census.qnt` assumes the trusted arithmetic checker
returns a per-shard primitive solution count of 0 for [2,72] and 1 for
[73,144], consistent with the independently checked corpus.

Each shard starts pending. A report can be submitted once; independent
inspection either verifies or rejects it. A publication is possible
only when every shard is verified, the partition constants agree
with the Lean mathematical partition, and none was rejected.
The safety property enforces sound verification and the absence of
premature publication. Concrete tests establish non-vacuous
successful publication and refusal of invalid/unverified reports.

The reported `Apalache --max-steps=6` result is **bounded model
checking**. It is not a theorem about all arbitrarily long traces.
The finite model has two shard IDs and deliberately small count values;
it does not model the arithmetic search itself.

## Toolchain and developer commands

`formal/toolchain.toml` pins Lean 4.34.1 with a SHA-256 verified archive,
Quint 0.33.0 via an npm integrity-locked package-lock, and Apalache
0.62.1 via a SHA-256 verified release archive. The pinning approach is
based on the established `larsbx/isnad-graph-lab` formal lane.
The download installer rejects wrong digests; the gate fails if any
tool, theorem, Quint test, or model checker fails.

On Linux x86-64 with Python 3.13, Node 22, Java 21 and network access:

```sh
bash tools/formal-setup.sh
bash tools/verify-formal.sh
```

GitHub Actions runs these same scripts on pushes and pull requests.
Changes to toolchain pins require explicit SHA-256 and lockfile review.

## E5v1 replay and trust boundary

`formal/lean/Replay.lean` is a compiled Lean executable that consumes
actual Mojo stdout in strict `CERT E5v1 ... / CENSUS B N` format.
It refuses noncanonical integers, false identities, out-of-range targets,
nonpositive bases, nonprimitive scaling, duplicate certificates, malformed
line boundaries, and incorrect footer record counts.

Lean replay checks soundness of each reported witness, NOT completeness.
An intentionally omitted-witness `CENSUS 144 0` report still passes replay.
The independent exact Mojo/Python census and bounded algorithm coverage
are separately required to support a complete-search claim.

Generic Lean `partition_cover` and `partition_disjoint` theorems
apply to any finite natural height range partitioned at `split+1`.

### Next proof obligations

1. Extend the congruence-sieve proof catalogue beyond moduli 11 and 25.
2. Establish a formally checked completeness bridge for the actual pair-index
   construction, rather than only the abstract complement identity.
3. Connect generic height-partition theorems to runtime-generated shard plans.
4. Extend Quint to cover crashes, retries, and deterministic reconciliation.

## Modular theorem development

`Modular.lean` formalizes finite fifth-power residue sets for 11 and 25,
and derives exact zero-count restrictions from the five-term equation.
The formal proof uses small finite-ring checks within Lean, not an imported
search output. `primitive_excludes_five` formally proves that if all five bases are
divisible by a prime-sized integer p > 1, the gcd cannot be 1.
Consequently, `primitive_11_count` and `primitive_5_count` establish
the **one-or-three divisibility law** for every primitive positive solution,
without a finite search bound. This is proof about the equation, not a
proof of E5-1 through E5-5.

## Quint crash/retry refinement (bounded)

`formal/quint/recovery.qnt` is an additional finite-state process model
for the two-shard certification controller. It tracks per-shard submission
tickets and imposes a maximum of two attempts. A worker crash returns a
submitted shard to pending without changing the ticket. Resubmission
increments the ticket; inspection requires the current ticket, so a late
callback from an old attempt cannot certify the new one. Once checked,
a shard becomes verified or rejected and cannot revert to pending.

Safety properties require valid partition endpoints, bounded tickets,
correctly validated per-shard claims and publication only after every
shard is verified. Executable Quint tests cover successful recovery,
stale-ticket rejection, false results, attempt exhaustion and attempted
crashes of finalized shards. Apalache checks this finite model through four transitions;
the separate Quint executable test exercises a longer successful
crash/retry-and-publication trace for non-vacuity.

**Limitations:** the real deployment may have an unbounded number of
retries, more than two partitions, and network failures outside this
model. This is bounded safety verification, not proof of liveness or
end-to-end operational fault tolerance. Per-shard expected counts are
assumptions sourced from the independent arithmetic checker.

## Abstract pair-index completeness

`formal/lean/PairIndex.lean` defines the finite mathematical list of every
ordered pair `1 ≤ a ≤ b < e`, with its exact fifth-power sum. Its Lean
proofs establish that every such pair is present and every valid primitive
positive E5 solution has the complementary pair sum in the list. This
strengthens the earlier arithmetic complement identity and eliminates
an abstract omission risk. The **implementation refinement** from Mojo's
sorted integer array and binary search to the formal list is still an
open proof obligation. Likewise, the theoretical index carries no
claims about the asymptotic distribution of solutions.

## Sorted index membership refinement and runtime conformance

`formal/lean/SortedIndex.lean` proves sorting the complete mathematical
fifth-power pair-sum list is membership-preserving, and proves a decidable
sorted-list membership test accepts every complement of a valid solution.
This is a kernel-checked sorting **specification** theorem, not a proof of
Mojo's particular memory layout, `sort` implementation, or binary-search
loop.

The exact `contains_sorted` production routine has been isolated into
`kernel/pair_index.mojo` and is imported by the census as well as the
conformance executable. CI checks its actual compiled behavior for every
pair sum through height 24 (including duplicates), adjacent misses,
negative targets and the empty-list case, against an independent Python set.
The binary search is used only as a necessary membership prefilter; the
positive E5 census reconstructs **all** `a ≤ b ≤ c` representations
rather than relying on a single recovered pair.

**Assurance:** sorted mathematical membership is proved for all heights;
the Mojo implementation is regression-tested only on a bounded input domain.
A universal cross-language compiler-level refinement proof is still open.

## Universal sorted-index pruning lemmas

`formal/lean/BinarySearch.lean` establishes, for every sorted list and
arbitrary pivot and target, that when the pivot is below the target no
entry at or before the pivot can match. When the pivot is above the
target, no entry at or after the pivot can match. Equality at the pivot
provides a sound membership witness. These are checked by Lean without
any finite search-height restriction. Together with sorted membership
preservation and 6,971 compiled Mojo regression queries, these close
the mathematical branch-pruning obligations but do **not** prove
bounds arithmetic, termination, or compiler-level refinement of the
concrete binary-search implementation.

## Lower-bound interval invariant

`LowerBoundInvariant.lean` establishes the mathematical loop invariant:
all entries before `lo` are strictly below the search target, and all
entries at/after `hi` are greater than or equal to it. The initial
window satisfies it, and both branches preserve it, with a strictly
smaller finite search interval. At a completed window (`lo = hi`) the
pivot equality check is equivalent to membership in the original list.
The proofs apply to all sorted natural-number lists, including duplicates.
They do not establish compiler-level refinement of the actual Mojo while
loop or prove arbitrary machine arithmetic cannot overflow.
