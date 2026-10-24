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
(cd formal/quint && npx --no-install quint typecheck census.qnt)
(cd formal/quint && npx --no-install quint test census.qnt --backend "$(pin quint backend)" --seed "$(pin quint seed)")
(cd formal/quint && npx --no-install quint run census.qnt \
  --backend "$(pin quint backend)" --seed "$(pin quint seed)" \
  --invariant=safety --max-samples=200 --max-steps=6 --verbosity=1)
(cd formal/quint && npx --no-install quint verify census.qnt \
  --invariant=safety --apalache-version "$(pin apalache version)" \
  --max-steps "$(pin apalache max_steps)" --verbosity=1)
echo "Lean and Quint formal gate passed."
