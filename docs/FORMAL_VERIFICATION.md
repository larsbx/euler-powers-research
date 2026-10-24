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

1. Prove fifth-power residue restrictions modulo 11 and 25 within Lean,
   not merely by executing the finite-ring Mojo/Python agreement test.
2. Bridge canonical E5v1 certificate parsing and identity acceptance to
   Lean-certified replay of actual Mojo output.
3. Specify arbitrary complete height partitions instead of only the
   initial two-shard instance.
4. Extend the Quint admission model to signed certificates and
   crash/retry/reconciliation without weakening its safety boundary.
