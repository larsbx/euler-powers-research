"""Controlled native comparison of P4 m=2475 and P5 m=99000.

The two historical/candidate sources compile with the same immutable
shared Mojo dependency and pinned toolchain. Both raw streams are replayed
against the independent full Python candidate oracle and digest root.
The result is a machine-local observation, not a general speedup claim.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from statistics import median
from tempfile import TemporaryDirectory
from time import perf_counter_ns
import argparse
import json
import platform
import subprocess

from benchmark_pair_index import ROOT, run, compile_mojo
from replay_partition import replay
from test_pair_partition import oracle, expected_stream
from collections import Counter

BASELINE_SHA = "5de9573ab831f2a1e47cbb1efd0c089f1aa253c8"
PINNED_ROOT = "5b8ed68d8512bb11bf4ac57e2f79657e65893427c157c0615b784d86671af482"
DOMAIN = (48, 144)
REPS = 7


def sample(binary: Path, bound: int, scratch: Path, tag: str, trial: int):
    time_path = scratch / f"{tag}-{bound}-{trial}.txt"
    started = perf_counter_ns()
    proc = subprocess.run([
        "/usr/bin/time", "-f", "%e %M", "-o", str(time_path),
        str(binary), str(bound), "35",
    ], capture_output=True, cwd=ROOT, check=True)
    elapsed_ns = perf_counter_ns() - started
    wall_seconds, rss_kib = time_path.read_text().split()
    records = proc.stdout.decode("ascii").splitlines()
    assert Counter(records) == expected_stream(bound, 35), "native stream differs from exact oracle"
    refparts, refcerts = oracle(bound, 35)
    replayed = replay(records, bound, 35, refparts, refcerts,
                      PINNED_ROOT if bound == 144 else None)
    return {
        "engine": tag,
        "height": bound,
        "trial": trial,
        "elapsed_ns_including_gnu_time_launch": elapsed_ns,
        "gnu_time_wall_seconds": float(wall_seconds),
        "peak_rss_kib": int(rss_kib),
        "canonical_stream_sha256": sha256(proc.stdout).hexdigest(),
        "root": replayed["root_sha256"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=ROOT / "benchmarks/results/modulus-selection.json")
    args = parser.parse_args()
    assert platform.system() == "Linux" and Path("/usr/bin/time").exists()
    assert run("git", "cat-file", "-t", BASELINE_SHA).strip() == b"commit"
    source_old = run("git", "show", f"{BASELINE_SHA}:kernel/pair_partition.mojo")
    source_new = (ROOT / "kernel/pair_partition.mojo").read_bytes()
    with TemporaryDirectory() as t:
        folder = Path(t)
        path_old = folder / "p4.mojo"
        path_old.write_bytes(source_old)
        bin_old, bin_new = folder / "p4", folder / "p5"
        compile_mojo(path_old, bin_old)
        compile_mojo(ROOT / "kernel/pair_partition.mojo", bin_new)
        all_rows = []
        for bound in DOMAIN:
            for trial in range(REPS):
                engines = (("p4_2475", bin_old), ("p5_99000", bin_new))
                if trial % 2:
                    engines = engines[::-1]
                for tag, binary in engines:
                    row = sample(binary, bound, folder, tag, trial)
                    all_rows.append(row)
                    print(f"B={bound} {tag} trial={trial}: "
                          f"{row['elapsed_ns_including_gnu_time_launch']} ns, "
                          f"peak={row['peak_rss_kib']} KiB")
        summary = []
        for bound in DOMAIN:
            for tag in ("p4_2475", "p5_99000"):
                rows = [r for r in all_rows if r["height"] == bound and r["engine"] == tag]
                summary.append({
                    "height": bound, "engine": tag,
                    "median_elapsed_ns": int(median(r["elapsed_ns_including_gnu_time_launch"] for r in rows)),
                    "median_rss_kib": int(median(r["peak_rss_kib"] for r in rows)),
                    "median_gnu_time_wall_seconds": median(r["gnu_time_wall_seconds"] for r in rows),
                })
    record = {
        "schema": "E5-MODULUS-SELECTION-v1",
        "source_p4_sha256": sha256(source_old).hexdigest(),
        "source_p5_sha256": sha256(source_new).hexdigest(),
        "commit_baseline": BASELINE_SHA,
        "commit_candidate": run("git", "rev-parse", "HEAD").decode().strip(),
        "mojo_version": run("mojo", "--version").decode().strip(),
        "platform": platform.platform(),
        "wall_measurement": "Python perf_counter_ns around GNU /usr/bin/time subprocess; includes process creation",
        "notes": "identical domain and full independent exact oracle per native run; no performance guarantee",
        "samples": all_rows,
        "summary": summary,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(f"Saved exact verified timing artifact at {args.output}")


if __name__ == "__main__":
    main()
