# Mojo-first executable arithmetic (M1)

The primary executable acceptance check for known Euler fifth-power identities
is `kernel/verify_known.mojo`. Its `BigZ` and `gcd_i64` implementations are
**imported from** `larsbx/finite-math-kernels` at immutable commit
`d4445ff59e7b5036081f56f066525ad7b60003fe` (2026-10-24).
No fork of the shared exact-arithmetic kernel is maintained here.

## Commands

On Linux x86-64 with Git, run:

```sh
pixi run --locked verify
```

The command fetches the pinned dependency into ignored `.deps/` (once), checks
the checkout SHA, invokes the pinned Mojo compiler to verify the CSV, and runs
the independent Python integer oracle. A missing compiler or failed dependency
pin **fails** rather than silently falling back to Python. CI gates both lanes
under `.github/workflows/mojo.yml`.

Mojo parses `data/known_solutions.csv` directly; it does not accept a Python
generated verdict. Every row must pass exact BigZ fifth-power equality,
primitivity, signed-vs-positive classification, and the proved prime-5/prime-11
divisibility conditions. Signed examples are admitted as examples without
becoming positive solutions. The bounded textual intake accepts bases with
absolute value <= 1,000,000,000; BigZ powers have no corresponding 64-bit
overflow. Larger inputs require an explicit parser bound update and tests.

## Authority and evidence

- **Mojo / finite-math-kernels:** primary native exact identity checker,
  finite residue sieves, future bounded searches and certificate replay.
- **Python:** independent reference/oracle and research orchestration; it is
  not a substitute for a missing native Mojo check.
- **Conjectures:** remain OPEN, HEURISTIC or CONJECTURAL; executable passes do
  not prove infinitude, density, or a search's exhaustiveness.

Follow the existing finite-math-kernels conformance-vector and provenance
discipline for subsequent enumeration work. Each exhaustive-search claim must
state its height bound, positive/signed domain, toolchain and dependency SHA,
output digest, and completeness argument. Numerical speedups require matched
hardware and validation before they are claimed.

The repo has a committed transitive `pixi.lock` for `linux-64`,
generated on GitHub Actions using the pinned `pixi.toml` manifest.
CI uses `pixi run --locked` to reject lockfile drift. The shared
`finite-math-kernels` repository is separately pinned by full Git SHA.
Reproducibility is scoped to this platform and these pinned inputs;
it does not imply cross-platform bitwise equality.

## P0 reusable exact-arithmetic adapter

See [the exact arithmetic bridge](EXACT_ARITHMETIC_BRIDGE.md). Native
checked powers, sums, signed complements, radix packing and GCD now pass
through one Euler adapter over the immutable upstream arithmetic kernels;
BigZ handles known signed solution verification without machine narrowing.
`verify_mojo.sh` calls `run_mojo.sh`, so both native commands use one
authoritative dependency pin. No bound or result is automatically widened.

## Exact bounded research kernels

See [the computational completeness contract](BOUNDED_SEARCH.md).
The pinned environment also provides `pixi run verify-research`,
which compares exact Mojo finite-ring DP and the full positive search
through height 144 against separate Python reference implementations.
Both are required by native CI. The original `verify` lane retains
unbounded `BigZ` checks for the published identities.

## Pair-sum residue partition milestone

The small positive-domain partition prototype, source-level Lean coverage and
multiplicity proofs, independent Python conformance checks and deterministic
manifest are described in [the partition contract](PAIR_PARTITION.md).
