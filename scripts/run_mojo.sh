#!/usr/bin/env bash
# Pin shared mathematical primitives by exact Git commit; refuse drift.
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ $# -lt 1 ]]; then
  echo "usage: run_mojo.sh <Mojo source> [args...]" >&2
  exit 2
fi
PIN="c5b2d3d7879bcf2354d4d9784bd20a6b3dc610fd"
UPSTREAM="https://github.com/larsbx/finite-math-kernels.git"
TARGET=".deps/finite-math-kernels"
if [[ ! -d "$TARGET/.git" ]]; then
  mkdir -p "$TARGET"
  git -C "$TARGET" init -q
  git -C "$TARGET" remote add origin "$UPSTREAM"
  git -C "$TARGET" fetch -q --depth=1 origin "$PIN"
  git -C "$TARGET" checkout -q --detach "$PIN"
fi
ACTUAL="$(git -C "$TARGET" rev-parse HEAD)"
if [[ "$ACTUAL" != "$PIN" ]]; then
  echo "Dependency drift: expected $PIN; got $ACTUAL" >&2
  exit 1
fi
mojo run -I kernel -I "$TARGET/kernel" "$@"
