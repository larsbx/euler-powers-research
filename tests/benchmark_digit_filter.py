"""Same-host prefilter-vs-no-prefilter wall/RSS comparison.

The archived P3 source is compiled with the SAME pinned Mojo and shared
kernel checkout as the proposed filtered implementation. Every native
stream is checked against the exact independent Python oracle and
unchanged partition SHA root before any timings are reported.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from statistics import median
from tempfile import TemporaryDirectory
import argparse
import json
import platform

from benchmark_pair_index import ROOT, run, compile_mojo, measure

PREFILTER_BASELINE_SHA = "d42cfa6a81a76dd8db973c92dc6efa5b6e518690"
DOMAINS = (48, 144)
TRIALS = 3


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=ROOT / "benchmarks/results/digit-filter-comparison.json")
    args = parser.parse_args()
    assert platform.system() == "Linux" and Path("/usr/bin/time").exists()
    assert (ROOT / ".deps/finite-math-kernels/kernel").is_dir()
    assert run("git", "cat-file", "-t", PREFILTER_BASELINE_SHA).strip() == b"commit"
    baseline_source = run("git", "show", f"{PREFILTER_BASELINE_SHA}:kernel/pair_partition.mojo")
    filtered_source = (ROOT / "kernel/pair_partition.mojo").read_bytes()
    with TemporaryDirectory() as tmp:
        scratch = Path(tmp)
        historical = scratch / "original_p3.mojo"
        historical.write_bytes(baseline_source)
        before = scratch / "baseline"
        after = scratch / "filtered"
        compile_mojo(historical, before)
        compile_mojo(ROOT / "kernel/pair_partition.mojo", after)
        samples = []
        for bound in DOMAINS:
            for trial in range(TRIALS):
                engines = (
                    (("baseline_p3", before), ("filtered_p4", after))
                    if trial % 2 == 0 else
                    (("filtered_p4", after), ("baseline_p3", before))
                )
                for name, binary in engines:
                    row = measure(binary, bound, scratch, name, trial)
                    samples.append(row)
                    print(
                        f"B={bound} {name} trial={trial}: "
                        f"wall={row['wall_seconds_gnu_time']}s "
                        f"max_rss_kib={row['peak_rss_kib_gnu_time']}"
                    )
    summaries = []
    for bound in DOMAINS:
        for name in ("baseline_p3", "filtered_p4"):
            group = [r for r in samples if r["height"] == bound and r["engine"] == name]
            assert len(group) == TRIALS
            summaries.append({
                "height": bound,
                "engine": name,
                "median_wall_seconds": median(r["wall_seconds_gnu_time"] for r in group),
                "median_peak_rss_kib": median(r["peak_rss_kib_gnu_time"] for r in group),
                "partition_digest_root_sha256": group[0]["partition_digest_root_sha256"],
                "reported_positive_complement_visits": group[0]["reported_positive_complement_visits"],
            })
    result = {
        "schema": "E5DIGIT-NATIVE-BENCH-v1",
        "baseline_commit": PREFILTER_BASELINE_SHA,
        "baseline_source_sha256": sha256(baseline_source).hexdigest(),
        "candidate_source_sha256": sha256(filtered_source).hexdigest(),
        "candidate_commit": run("git", "rev-parse", "HEAD").decode().strip(),
        "platform": platform.platform(),
        "mojo_version": run("mojo", "--version").decode().strip(),
        "meaning": "same-run GNU time wall seconds and Linux max RSS KiB; no speedup claim",
        "samples": samples,
        "summary": summaries,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {args.output}. All outputs match exact Python and pinned digest.")


if __name__ == "__main__":
    main()
