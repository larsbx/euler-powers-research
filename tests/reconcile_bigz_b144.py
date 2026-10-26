"""Independent cross-engine reconciliation of a COMPLETED native BigZ 2..144 plan.

Requires every exact Mojo height-shard transcript and its accepted P8
receipt. Reassembles real native rows into historical E5PARTv1 form,
checks all legacy pinned rows, per-key SHA root and canonical stream
digest. No synthetic or oracle-generated transcripts are substituted.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import bigz_shard_plan as shard
from replay_partition import replay

MANIFEST = ROOT / "certificates/pair_partition_e144_m35.json"
ROOT_144 = "5b8ed68d8512bb11bf4ac57e2f79657e65893427c157c0615b784d86671af482"
KNOWN_WITNESS = (27, 84, 110, 133, 144)


def reconcile(folder: Path, *, emit: bool = True) -> dict:
    plan = shard.load_canonical(folder / "plan.json")
    shard.check_plan(plan)
    if plan["last_height"] != 144 or plan["modulus"] != 35:
        raise ValueError("legacy reconciliation only accepts the B144/M35 domain")
    verified = shard.validate_acceptance(folder, plan, 1048576)
    if (folder / "accepted.json").read_bytes() != shard.canonical(verified):
        raise ValueError("missing or inconsistent full-height acceptance")
    legacy = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert legacy["schema"] == "E5PART-MANIFEST-v1"
    assert legacy["domain"]["max_e"] == 144 and legacy["domain"]["modulus"] == 35
    actual = ["DOMAIN E5PARTv1 144 35"]
    for a, b in map(tuple, plan["intervals"]):
        lines = (folder / (shard.filename(a, b) + ".txt")).read_text(
            encoding="ascii"
        ).splitlines()
        if lines[0] != f"DOMAIN E5BIGSHARDv1 {a} {b} 35":
            raise ValueError("invalid native shard domain")
        actual.extend(lines[1:-1])
    actual.append(f"TOTAL {len(verified['certificates'])}")
    reference_parts = [tuple(row) for row in legacy["partitions"]]
    report = replay(
        actual, 144, 35, reference_parts, [KNOWN_WITNESS], ROOT_144
    )
    stream_data = ("E5PART-STREAM-v1\n" + "\n".join(sorted(actual)) + "\n").encode("ascii")
    stream_digest = sha256(stream_data).hexdigest()
    if stream_digest != legacy["canonical_stream_sha256"]:
        raise ValueError("assembled BigZ stream differs from historical canonical stream")
    if (report["partition_rows"], report["right_pair_visits"],
            report["certificates"]) != (2574, 475063, 1):
        raise ValueError("unexpected complete BigZ B144 census statistics")
    if verified["right_pair_visits"] != report["right_pair_visits"]:
        raise ValueError("BigZ plan visits diverge from historical partition count")
    witness_text = "CERT E5v1 " + " ".join(map(str, KNOWN_WITNESS))
    if verified["certificates"] != [witness_text]:
        raise ValueError("BigZ accepted witnesses disagree with independently known witness")
    record = {
        "schema": "E5-BIGZ-B144-CROSSCHECK-v1",
        "scope": verified["scope"], "plan_sha256": verified["plan_sha256"],
        "accepted_sha256": shard.digest(shard.canonical(verified)),
        "shard_count": verified["shards"],
        "partition_rows": report["partition_rows"],
        "right_pair_visits": report["right_pair_visits"],
        "certificates": verified["certificates"],
        "historical_root_sha256": ROOT_144,
        "historical_canonical_stream_sha256": stream_digest,
        "comparison": "actual native BigZ streams vs historical packed-index rows and independent full per-shard integer oracle",
    }
    if emit:
        print(
            "CROSSCHECK complete BigZ 2..144, M=35: "
            f"{record['shard_count']} verified shards; 2574 rows; "
            "475063 visits; one primitive witness; pinned root and "
            "canonical historical stream MATCH"
        )
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = reconcile(args.directory.resolve())
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        shard.atomic(args.output, shard.canonical(result))


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, ValueError) as error:
        print(f"CROSSCHECK REFUSED: {error}", file=sys.stderr)
        raise SystemExit(1)
