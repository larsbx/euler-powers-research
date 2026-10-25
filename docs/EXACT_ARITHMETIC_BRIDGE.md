# P0 — exact arithmetic bridge to finite-math-kernels

## Scope and dependency authority

The native E5 implementation imports canonical arithmetic from
`larsbx/finite-math-kernels`, pinned **once** in
`scripts/run_mojo.sh` at immutable commit
`d4445ff59e7b5036081f56f066525ad7b60003fe`.
`scripts/verify_mojo.sh` reuses this same resolver; the checkout is
verified and never silently updated. Mojo is pinned separately by
`pixi.lock`. No upstream files are copied into this repository.

`kernel/euler_exact.mojo` is an Euler-specific *adapter*, not a fork
of shared arithmetic. Its public operations are:

| Adapter | Authoritative implementation | Contract |
| --- | --- | --- |
| `fifth_int(x)` | `finite_exact.checked_int.checked_mul` | Exact signed fifth power or explicit overflow refusal. |
| `pair_sum(x,y)` | `checked_add` | Exact pair sum or explicit overflow refusal. |
| `complement(e5,c5,d5)` | `checked_sub` | Exact signed complement, including negative results, or refusal. |
| `checked_pack_pair(value,a,b,stride)` | `checked_mul` / `checked_add` | Reject negative value, invalid radix/digits and overflow. |
| `primitive5(a,b,c,d,e)` | `finite_exact.integer_gcd.gcd_i64` | Exact five-base GCD=1 or refusal if GCD unrepresentable. |
| `fifth_bigz(x)` | `finite_exact.bigint_z` | Arbitrary-precision signed fifth power, with no narrowing to machine integer. |

**Machine contract:** `Int` is 64-bit on the pinned Linux target.
Each checked operation refuses overflows, not saturating, wrapping or
silently switching to floating point. The bounded E5 census still
requires `e<=1000`, and the packed-index partition still requires
`e<=144`, `M<=35`, fixed stride 145. Enlarging either search
requires a separate bounds/index argument; availability of BigZ
alone does **not** increase search coverage.

The known-solution verifier imports the *same* BigZ fifth-power adapter
and five-base primitivity function as the search code. It preserves the
separate signed-input policy (absolute base <=10^9) and still reports
the existing 4 primitive known identities / 2 strictly positive.
The bounded positive enumerator uses checked powers, pair sums,
complements and five-base GCD. The packed residue index uses checked
pair sums and canonical packed encoding/lookup.

## Executable conformance

`kernel/euler_exact_probe.mojo` exercises the actual pinned native
functions for exact signed powers through +/-6208, rejects +/-6209
because the fifth power is outside Int64, checks signed BigZ outputs
including +/-10^9, and tests addition overflow, complement underflow,
oversize packed records and out-of-range radix digits. It also
checks the primitive Lander–Parkin tuple and rejects its scaling.

`tests/test_euler_exact_bridge.py` independently computes the expected
values using Python's arbitrary-precision integer exponentiation and
`math.gcd`. It never produces a fallback acceptance verdict if Mojo
is missing or fails. The existing known-solutions, pair-index,
partition/digest and Lean/Quint regression suites remain required.

Run:

```sh
pixi run --locked verify
pixi run --locked verify-research
bash tools/verify-formal.sh
```

The formal lane also runs the native bridge probe. Existing Lean
`Int64Bounds` and `PackedPairIndex` prove the relevant *mathematical*
bounded envelopes; the cross-language implementation is separately
exercised and is not a compiler proof.

## Explicitly deferred work

- Modular-ring primitives and new prime-power or CRT sieve rules:
  separate theorem-backed PR. Do not confuse `Fp[p]` with `Z/p^kZ`.
  Hensel simple-root lifting cannot be assumed for `x^5-u` modulo 5.
- `Q`, polynomial and projective geometry applications: later research
  milestones with explicit positivity/nonzero-denominator obligations.
- Proven performance gain, expanded `B`, replicated Braun search
  coverage, verified native compiler semantics or conjecture closure:
  none are asserted by this bridge.
- Proof-record and signed-run provenance: future evidence-plane work,
  not part of the hot arithmetic operations.

**Trust boundary:** A correct exact identity confirms a reported
witness. Independent bounded verification and mathematical completeness
arguments are separate. A hashed transcript by itself cannot establish
that an exhaustive enumerator omitted no candidates.
