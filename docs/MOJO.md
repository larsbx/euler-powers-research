# Mojo-first executable arithmetic (M1)

The primary executable acceptance check for known Euler fifth-power identities
is `kernel/verify_known.mojo`. Its `BigZ` and `gcd_i64` implementations are
**imported from** `larsbx/finite-math-kernels` at immutable commit
`d4445ff59e7b5036081f56f066525ad7b60003fe` (2026-10-24).
No fork of the shared exact-arithmetic kernel is maintained here.

## Commands

On Linux x86-64 with Git, run:

```sh
pixi run verify
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

The repo currently has a pinned top-level Mojo dependency manifest, but no
checked-in transitive Pixi lock. Treat environment resolution as not fully
reproducible until a platform lock is generated and committed. This limitation
is not hidden by CI.
