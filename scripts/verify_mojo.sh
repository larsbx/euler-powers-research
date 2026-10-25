#!/usr/bin/env bash
# Use the single SHA-pinned dependency resolver for all native Mojo kernels.
set -euo pipefail
cd "$(dirname "$0")/.."
bash scripts/run_mojo.sh kernel/verify_known.mojo
