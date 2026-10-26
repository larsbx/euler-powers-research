"""Independent cross-domain reconciliation of an ACTUALLY completed B320 BigZ run.

Every raw native shard is re-enumerated via the independently implemented
Python exact full ordered-pair oracle before this process reads it.
Separate legacy B144/B256 roots and the new B320 root commit to the
actual native PART and CERT rows, without replacing them by oracle data.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys
import argparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import bigz_shard_plan as shard
from replay_partition import replay
from test_pair_partition import oracle as independent_packed_oracle

LEGACY_144 = ROOT / "certificates/pair_partition_e144_m35.json"
ROOT_144 = "5b8ed68d8512bb11bf4ac57e2f79657e65893427c157c0615b784d86671af482"
ROOT_256 = "157fdbc83048ddc782d8aa04c9691d0c34dabfaf96819a6976dd6671e284e07e"
ROOT_320 = "729a29fdb2c6bc391a22748831e324963f532aa093f294f3a88f2d85eaf69681"
WITNESS = (27, 84, 110, 133, 144)
WITNESS_LINE = "CERT E5v1 " + " ".join(map(str, WITNESS))


def reassemble(folder: Path, plan: dict) -> list[str]:
    """Only reads actual Mojo lines already validated independently."""
    records: list[str] = []
    for a, b in map(tuple, plan["intervals"]):
        lines = (folder / (shard.filename(a, b) + ".txt")).read_text(
            encoding="ascii"
        ).splitlines()
        if not lines or lines[0] != f"DOMAIN E5BIGSHARDv1 {a} {b} 35":
            raise ValueError("invalid native BigZ shard header")
        records.extend(lines[1:-1])
    return records


def projected(records: list[str], bound: int) -> list[str]:
    """Lossless prefix projection of already-verified PART and CERT records."""
    rows: list[str] = []
    witnesses = 0
    for line in records:
        columns = line.split(" ")
        if columns[0] == "PART":
            if int(columns[1]) <= bound:
                rows.append(line)
        elif columns[:2] == ["CERT", "E5v1"]:
            if int(columns[-1]) <= bound:
                rows.append(line)
                witnesses += 1
        else:
            raise ValueError(f"unsupported BigZ shard record: {line!r}")
    return [f"DOMAIN E5PARTv1 {bound} 35", *rows, f"TOTAL {witnesses}"]


def reconcile(folder: Path) -> dict:
    plan = shard.load_canonical(folder / "plan.json")
    shard.check_plan(plan)
    if plan["last_height"] != 320 or plan["modulus"] != 35 or plan["max_heights_per_shard"] != 4:
        raise ValueError("B320 audit demands exact complete 2..320/M35 width-four plan")
    accepted = shard.validate_acceptance(folder, plan, 1048576)
    if (folder / "accepted.json").read_bytes() != shard.canonical(accepted):
        raise ValueError("inconsistent accepted BigZ B320 receipts")
    if accepted["shards"] != 80 or accepted["certificates"] != [WITNESS_LINE]:
        raise ValueError("unverified complete B320 cardinality or changed witnesses")
    rows = reassemble(folder, plan)
    legacy = json.loads(LEGACY_144.read_text(encoding="utf-8"))
    outcomes: list[dict] = []
    for bound in (144, 256, 320):
        projected_lines = projected(rows, bound)
        if bound == 144:
            expected_parts = [tuple(x) for x in legacy["partitions"]]
            expected_certs = [WITNESS]
        elif bound == 256:
            expected_parts, expected_certs = independent_packed_oracle(256, 35)
        else:
            # Every B320 PART and CERT row was independently enumerated
            # for the exact native interval by shard.validate_acceptance.
            expected_parts = None
            expected_certs = [WITNESS]
        root = ROOT_144 if bound == 144 else ROOT_256 if bound == 256 else ROOT_320
        report = replay(projected_lines, bound, 35,
                        expected_parts, expected_certs, root)
        if report["certificates"] != 1:
            raise ValueError("invalid positive primitive witness count")
        if report["partition_rows"] != 18 * (bound - 1):
            raise ValueError("missing or duplicated canonical partition")
        outcome = {
            "bound": bound,
            "partition_rows": report["partition_rows"],
            "positive_right_pair_visits": report["right_pair_visits"],
            "certificates": report["certificates"],
            "root_sha256": report["root_sha256"],
        }
        if bound == 144:
            stream = ("E5PART-STREAM-v1\n" +
                      "\n".join(sorted(projected_lines)) + "\n").encode("ascii")
            if sha256(stream).hexdigest() != legacy["canonical_stream_sha256"]:
                raise ValueError("BigZ prefix B144 canonical stream differs from historical packed stream")
        if bound == 256 and report["right_pair_visits"] != 2664481:
            raise ValueError("B256 visits differ from independently checked packed search")
        if bound == 320 and report["right_pair_visits"] != 5201461:
            raise ValueError("B320 visits differ from independently replayed full Mojo search")
        outcomes.append(outcome)
    if accepted["right_pair_visits"] != outcomes[-1]["positive_right_pair_visits"]:
        raise ValueError("complete B320 visits differ from accepted plan")
    return {
        "schema": "E5-BIGZ-B320-COMPLETE-CROSSCHECK-v1",
        "plan_sha256": accepted["plan_sha256"],
        "accepted_sha256": shard.digest(shard.canonical(accepted)),
        "source": plan["source"],
        "shards": accepted["shards"],
        "scope": accepted["scope"],
        "witnesses": accepted["certificates"],
        "prefixes": outcomes,
        "method": "all actual native BigZ stdout independently replayed per shard; B144/B256 separately checked against packed-index roots",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("directory", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    record = reconcile(args.directory.resolve())
    for row in record["prefixes"]:
        print(f"VERIFIED B{row['bound']}: {row['partition_rows']} rows, "
              f"{row['positive_right_pair_visits']} positive right pairs, "
              f"{row['certificates']} primitive positive solutions, "
              f"root={row['root_sha256']}")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        shard.atomic(args.output, shard.canonical(record))


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, ValueError) as e:
        print(f"REFUSED B320 CROSSCHECK: {e}", file=sys.stderr)
        raise SystemExit(1)
