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

## Candidate reconstruction completeness

`Reconstruction.lean` models the finite `c≤d<e` and `a≤b≤c` loops
with exact pair-list predicates, applies the sorted pair-sum prefilter,
requires nonnegative fifth-power complement, and checks the **particular**
reconstructed pair's exact equality and primitivity. Lean proves the
resulting mathematical `StagedCandidate` predicate is equivalent to
`Valid` for every natural quintuple and every target height. Repeated
pair sums do not erase other representations: the reconstruction list
retains all qualifying pairs. The actual Mojo nested loops and its
compiler execution remain tested and require a separate refinement proof.

## Total verified Lean lower-bound loop

`CertifiedLowerBound.lean` implements an executable recursive lower-bound
search over a sorted natural-number list. Each recursive call has a
proof-carrying window invariant, and the interval width `hi-lo`
strictly decreases. Lean checks termination; the final result retains
the invariant, and `certifiedLowerBound_correct` proves that its final
index matches the target if and only if the target occurs anywhere in
the sorted list. This is valid for all finite lists and duplicate entries.
It provides a complete **Lean mathematical algorithm proof** corresponding
to the branch and midpoint rules in the Mojo implementation. Native Mojo
still requires independent compiler-level refinement to promote that
algorithm theorem into a whole-program guarantee.

## Signed-data compiled conformance expansion

The native lower-bound prefilter now also runs deterministic signed-list
test vectors independently of the Diophantine pair-sum corpus. A separate
Python set oracle checks arbitrary sorted inputs with duplicate runs,
negative values, the empty array and signed Int64 boundary values.
The *production* `contains_sorted` function is imported by the same Mojo
test driver, so the tests do not accidentally validate a different
implementation. This strengthens empirical compiler-level confidence;
a passing bounded test is not a universal refinement theorem.

## Generic contiguous-shard plan and Lean replay

`ShardPlan.lean` checks a sequence of exact closed integer intervals,
starting at height 2 and ending at the declared bound. The theorem
`validPlan_covers` proves **every** height in [2, B] belongs to a
declared interval whenever the executable plan checker accepts. Missing
heights, overlapping boundaries, extra heights and malformed plan
coordinates are rejected. The formal gate replays the actual Mojo
`census-shard-a` and `census-shard-b` outputs in the extended Lean
`replay shard` CLI and validates the concrete plan in `replay plan`.

Each shard's canonical start/end fields, count, primitive positive
identities and witness heights are checked independently. This closes
the **metadata/declared-coverage** boundary but not the possibility of
omitted arithmetic solutions within an individual shard; an empty but
well-formed report for [73,144] is still accepted by witness replay.
The separate, bounded independent Python census comparison and
mathematical candidate coverage remain essential.

Developer commands:
```sh
cd formal/lean
lake exe replay plan 144 2 72 73 144
lake exe replay shard /path/to/shard-a.txt 2 72
lake exe replay shard /path/to/shard-b.txt 73 144
```

## Bounded machine integer proof

`Int64Bounds.lean` establishes the precise finite arithmetic envelope
for the native search (`e≤1000`): all fifth powers, pair-sum entries,
and signed two-term complements are inside Int64's legal range. Negative
complements are explicitly modeled in `Int`, never saturated with
natural-number subtraction. The source uses multiplication of a
nonnegative base and the Lean theorem proves intermediate powers remain
bounded. CI also rejects malformed or out-of-range Mojo input.
Compiler-level correspondence of the native `Int64` implementation
remains an independent verification obligation.

## Observational correspondence: native Mojo lower-bound traces

`kernel/pair_index.mojo` now contains **one** lower-bound search body
used by both production `contains_sorted` and its trace-enabled entry.
The native `pair_index_trace_probe.mojo` emits a canonical transcript of
21 deterministic sorted signed-list cases (including empty, duplicate,
negative, fifth-power and 64-bit boundary inputs). Each CASE declares
its complete input; every STEP records its pre-transition bounds,
midpoint and pivot; STOP and RESULT record the termination state.

`formal/lean/TraceReplay.lean` independently checks the exact
signed-Int64 inputs, sortedness, initial state, every observed loop step,
midpoint and pivot, transition choice, total number of steps, terminal
partition invariant, first-match index, exact membership and output.
It rejects omitted, extra, reordered, forged or malformed steps. The
adversarial integration suite corrupts twelve transcript properties and
requires Lean to refuse each one. On valid traces, the producer also
checks that traced and production-untraced calls return the same answer.

**Assurance boundary:** This is a machine-checkable *finite observational
correspondence*, not a universal translation validation or compiler proof.
Lean verifies the trace **as emitted by the executable**; it cannot
establish that the executable did not conceal events, that a false input
vector was not claimed, or that every possible machine state was covered.
The next research step is stronger cross-language refinement / verified
interpreter or proof-carrying lower-level execution evidence.
