#!/usr/bin/env bash
# The SHA is the reviewed finite-math-kernels main commit of 2026-10-24.
# Mojo imports its canonical BigZ and Euclidean gcd, not copied arithmetic.
set -euo pipefail
cd "$(dirname "$0")/.."
PIN="d4445ff59e7b5036081f56f066525ad7b60003fe"
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
echo "finite-math-kernels @ $PIN"
mojo run -I kernel -I "$TARGET/kernel" kernel/verify_known.mojo
