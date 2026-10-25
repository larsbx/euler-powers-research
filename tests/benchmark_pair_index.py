"""Same-run native Mojo benchmark against the pinned merged P2 implementation.

No performance threshold: heterogeneous CI hosts and warm-up effects can
change timing. This script *executes* both binaries with the same toolchain,
and validates every output against the independent exact Python oracle.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
from statistics import median
from tempfile import TemporaryDirectory
import argparse
import json
import os
import platform
import subprocess
import sys

from replay_partition import replay
from test_pair_partition import oracle, expected_stream

ROOT = Path(__file__).resolve().parents[1]
BASELINE_SHA = "792e0e9ca70575c41202c81e47bd23a8dfc8d571"
MODULUS = 35
DOMAINS = (48, 144)
TRIALS = 3
PINNED_ROOT_144 = "5b8ed68d8512bb11bf4ac57e2f79657e65893427c157c0615b784d86671af482"


def run(*cmd: str) -> bytes:
    return subprocess.check_output(cmd, cwd=ROOT, stderr=subprocess.PIPE)


def compile_mojo(source: Path, output: Path) -> None:
    subprocess.run([
        "mojo", "build", "-I", "kernel",
        "-I", ".deps/finite-math-kernels/kernel",
        str(source), "-o", str(output),
    ], cwd=ROOT, check=True)


def measure(binary: Path, bound: int, scratch: Path, name: str, trial: int) -> dict:
    metrics_path = scratch / f"{name}-{bound}-{trial}.time"
    completed = subprocess.run([
        "/usr/bin/time", "-f", "%e %M", "-o", str(metrics_path),
        str(binary), str(bound), str(MODULUS)
    ], cwd=ROOT, capture_output=True, check=True)
    elapsed_text, rss_text = metrics_path.read_text().split()
    lines = completed.stdout.decode("ascii").splitlines()
    expected_parts, expected_certs = oracle(bound, MODULUS)
    assert Counter(lines) == expected_stream(bound, MODULUS), (
        f"{name}: independent P2 oracle mismatch at B={bound}"
    )
    report = replay(
        lines, bound, MODULUS, expected_parts, expected_certs,
        PINNED_ROOT_144 if bound == 144 else None,
    )
    return {
        "engine": name,
        "height": bound,
        "modulus": MODULUS,
        "trial": trial,
        "wall_seconds_gnu_time": float(elapsed_text),
        "peak_rss_kib_gnu_time": int(rss_text),
        "stream_sha256": sha256(completed.stdout).hexdigest(),
        "partition_digest_root_sha256": report["root_sha256"],
        "reported_positive_complement_visits": report["right_pair_visits"],
        "reported_primitive_certificates": report["certificates"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=ROOT / "benchmarks/results/native-comparison.json")
    args = parser.parse_args()
    assert platform.system() == "Linux", "Requires Linux GNU time KiB max RSS"
    assert Path("/usr/bin/time").exists()
    assert (ROOT / ".deps/finite-math-kernels/kernel").is_dir()
    assert run("git", "cat-file", "-t", BASELINE_SHA).strip() == b"commit", (
        "Historical P2 commit unavailable: checkout with fetch-depth: 0"
    )
    original_source = run("git", "show", f"{BASELINE_SHA}:kernel/pair_partition.mojo")
    current_source = (ROOT / "kernel/pair_partition.mojo").read_bytes()
    with TemporaryDirectory() as tmp:
        scratch = Path(tmp)
        previous = scratch / "baseline.mojo"
        previous.write_bytes(original_source)
        baseline_binary = scratch / "baseline"
        current_binary = scratch / "packed"
        compile_mojo(previous, baseline_binary)
        compile_mojo(ROOT / "kernel/pair_partition.mojo", current_binary)
        samples = []
        for bound in DOMAINS:
            for trial in range(TRIALS):
                engines = (
                    (("baseline_p2", baseline_binary), ("packed_p3", current_binary))
                    if trial % 2 == 0 else
                    (("packed_p3", current_binary), ("baseline_p2", baseline_binary))
                )
                for name, binary in engines:
                    sample = measure(binary, bound, scratch, name, trial)
                    samples.append(sample)
                    print(
                        f"B={bound} {name} trial={trial}: "
                        f"{sample['wall_seconds_gnu_time']}s, "
                        f"peak_rss={sample['peak_rss_kib_gnu_time']}KiB, "
                        f"visits={sample['reported_positive_complement_visits']}"
                    )
    summaries = []
    for bound in DOMAINS:
        for name in ("baseline_p2", "packed_p3"):
            subset = [s for s in samples if s["height"] == bound and s["engine"] == name]
            assert len(subset) == TRIALS
            summaries.append({
                "height": bound, "engine": name,
                "median_wall_seconds": median(s["wall_seconds_gnu_time"] for s in subset),
                "median_peak_rss_kib": median(s["peak_rss_kib_gnu_time"] for s in subset),
                "reported_positive_complement_visits": subset[0]["reported_positive_complement_visits"],
                "reported_primitive_certificates": subset[0]["reported_primitive_certificates"],
                "partition_digest_root_sha256": subset[0]["partition_digest_root_sha256"],
            })
    record = {
        "schema": "E5PAIR-NATIVE-BENCH-v1",
        "baseline_commit": BASELINE_SHA,
        "baseline_source_sha256": sha256(original_source).hexdigest(),
        "candidate_source_sha256": sha256(current_source).hexdigest(),
        "candidate_commit": run("git", "rev-parse", "HEAD").decode().strip(),
        "platform": platform.platform(),
        "mojo_version": run("mojo", "--version").decode(errors="replace").strip(),
        "measurement": "GNU /usr/bin/time wall-clock seconds, Linux max RSS KiB",
        "repetitions_per_domain_and_engine": TRIALS,
        "acceptance": "correctness only, no performance threshold or multi-host speedup claim",
        "summary": summaries,
        "samples": samples,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {args.output}; all native streams match independent oracle.")


if __name__ == "__main__":
    main()
