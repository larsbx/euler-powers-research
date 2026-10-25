#!/usr/bin/env bash
# Fail-closed formal gate: Lean kernel proofs + axiom audit, Quint tests,
# simulation, and Apalache bounded model checking. No optional skips in CI.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
pin() {
  python3 -c "import sys,tomllib; print(tomllib.load(open(sys.argv[3],'rb'))[sys.argv[1]][sys.argv[2]])" "$1" "$2" "$ROOT/formal/toolchain.toml"
}
export PATH="${EULER_FORMAL_CACHE:-$HOME/.cache/euler-formal}/$(pin lean dir)/bin:$PATH"
lean --version | grep -q "version $(pin lean version),"
(cd formal/lean && lake build)
(cd formal/lean && lake env lean Audit.lean)
(cd formal/lean && lake build replay)
python3 tests/test_lean_replay.py
python3 tests/test_lean_shards.py
(cd formal/lean && lake build trace-replay)
pixi run --locked trace-conformance
pixi run --locked pair-index-conformance

# Replay the actual Mojo stdout, never a Python-reconstructed replacement.
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT
pixi run --locked census-144 > "$tmp"
cmp certificates/census_e144.txt "$tmp"
(cd formal/lean && lake exe replay "$tmp" 144)

# Recompute actual independent Mojo shard streams and replay both through
# Lean. Verify that the *declared* plan covers every height without gaps.
tmp_lo="$(mktemp)"
tmp_hi="$(mktemp)"
trap 'rm -f "$tmp" "$tmp_lo" "$tmp_hi"' EXIT
pixi run --locked census-shard-a > "$tmp_lo"
pixi run --locked census-shard-b > "$tmp_hi"
(cd formal/lean && lake exe replay plan 144 2 72 73 144)
(cd formal/lean && lake exe replay shard "$tmp_lo" 2 72)
(cd formal/lean && lake exe replay shard "$tmp_hi" 73 144)
(cd formal/quint && npx --no-install quint typecheck census.qnt)
(cd formal/quint && npx --no-install quint test census.qnt --backend "$(pin quint backend)" --seed "$(pin quint seed)")
(cd formal/quint && npx --no-install quint run census.qnt \
  --backend "$(pin quint backend)" --seed "$(pin quint seed)" \
  --invariant=safety --max-samples=200 --max-steps=6 --verbosity=1)
(cd formal/quint && npx --no-install quint verify census.qnt \
  --invariant=safety --apalache-version "$(pin apalache version)" \
  --max-steps "$(pin apalache max_steps)" --verbosity=1)

# Recovery model: bounded worker crashes, monotonic submission tickets,
# rejection of stale callbacks, and publication only after independent checks.
(cd formal/quint && npx --no-install quint typecheck recovery.qnt)
(cd formal/quint && npx --no-install quint test recovery.qnt \
  --backend "$(pin quint backend)" --seed "$(pin quint seed)")
(cd formal/quint && npx --no-install quint run recovery.qnt \
  --backend "$(pin quint backend)" --seed "$(pin quint seed)" \
  --invariant=safety --max-samples=300 --max-steps=8 --verbosity=1)
(cd formal/quint && npx --no-install quint verify recovery.qnt \
  --invariant=safety --apalache-version "$(pin apalache version)" \
  --max-steps=4 --verbosity=1)
echo "Lean and Quint formal gate passed."
