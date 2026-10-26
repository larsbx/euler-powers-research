#!/usr/bin/env bash
# Physical memory bound: Mojo/tcmalloc reserves large virtual address ranges.
# A systemd cgroup accounts the entire controller/native/replay process tree.
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ $# -eq 0 ]]; then
  echo 'usage: run_research_cgroup.sh COMMAND [ARGS...]' >&2
  exit 2
fi
exec sudo systemd-run --wait --pipe --collect --service-type=exec \
  --uid="$(id -u)" --gid="$(id -g)" \
  --property=MemoryAccounting=yes --property=MemoryMax=2G \
  --property=MemorySwapMax=0 --property=RuntimeMaxSec=1200 \
  --property="WorkingDirectory=$PWD" \
  --setenv="PATH=$PATH" \
  --setenv="GITHUB_SHA=${GITHUB_SHA:-local-uncommitted}" \
  --setenv="GITHUB_RUN_ID=${GITHUB_RUN_ID:-local}" \
  "$@"
