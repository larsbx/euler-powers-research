"""Fail-closed, gap-free E5 BigZ height-shard execution and replay.

Only ACCEPTED, independently replayed exact Mojo stdout contributes to
the final finite 2..B receipt. Hashes provide integrity, not provenance
or authenticity. A claimed complete PLAN is not an accepted census.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from math import gcd
import os
from pathlib import Path
import re
import resource
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic_ns

ROOT = Path(__file__).resolve().parents[1]
NAT = re.compile(r"(0|[1-9][0-9]*)\Z", re.ASCII)
SCHEMA = "E5BIG-PLAN-v1"
RECEIPT = "E5BIG-RECEIPT-v1"
ACCEPTANCE = "E5BIG-ACCEPTED-v1"


def canonical(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def natural(s: str) -> int:
    if NAT.fullmatch(s) is None:
        raise ValueError(f"noncanonical positive decimal {s!r}")
    return int(s)


def valid_domain(bound: int, width: int, modulus: int) -> None:
    if not (2 <= bound <= 320 and 1 <= width <= 4 and 2 <= modulus <= 35):
        raise ValueError("require 2<=B<=320, 1<=width<=4, 2<=M<=35")


def intervals(bound: int, width: int) -> list[tuple[int, int]]:
    if not (2 <= bound <= 320 and 1 <= width <= 4):
        raise ValueError("invalid plan domain")
    return [(start, min(start + width - 1, bound))
            for start in range(2, bound + 1, width)]


def check_intervals(ranges: list[list[int]], bound: int, width: int) -> None:
    if (not isinstance(ranges, list) or
        any(not isinstance(r, list) or len(r) != 2 or
            any(type(x) is not int for x in r) for r in ranges) or
        ranges != [list(pair) for pair in intervals(bound, width)]):
        raise ValueError("missing, overlapping, reordered or excess height shard")


def dependency_pin() -> str:
    text = (ROOT / "scripts/run_mojo.sh").read_text()
    match = re.search(r'^PIN="([a-f0-9]{40})"$', text, re.M)
    if not match:
        raise ValueError("missing immutable finite-math-kernels pin")
    return match.group(1)


def source_context() -> dict:
    return {
        "mojo_sha256": digest((ROOT / "kernel/bigz_shard.mojo").read_bytes()),
        "index_sha256": digest((ROOT / "kernel/bigz_pair_index.mojo").read_bytes()),
        "verifier_sha256": digest(Path(__file__).read_bytes()),
        "pixi_lock_sha256": digest((ROOT / "pixi.lock").read_bytes()),
        "finite_math_kernels_pin": dependency_pin(),
    }


def make_plan(bound: int, width: int, modulus: int) -> dict:
    valid_domain(bound, width, modulus)
    return {
        "schema": SCHEMA, "first_height": 2, "last_height": bound,
        "max_heights_per_shard": width, "modulus": modulus,
        "intervals": [list(pair) for pair in intervals(bound, width)],
        "source": source_context(),
    }


def check_plan(plan: dict) -> None:
    if set(plan) != {"schema", "first_height", "last_height",
                     "max_heights_per_shard", "modulus", "intervals", "source"}:
        raise ValueError("unexpected plan fields")
    if plan["schema"] != SCHEMA or plan["first_height"] != 2:
        raise ValueError("unknown or non-2-based plan")
    bound, width, modulus = (plan[k] for k in
        ("last_height", "max_heights_per_shard", "modulus"))
    if not all(type(x) is int for x in (bound, width, modulus)):
        raise ValueError("noninteger plan bounds")
    valid_domain(bound, width, modulus)
    check_intervals(plan["intervals"], bound, width)
    if plan["source"] != source_context():
        raise ValueError("stale or wrong-source shard plan")


def oracle(start: int, end: int, modulus: int) -> bytes:
    """Independent unrestricted exact integer enumeration, no residue sieve."""
    if not (2 <= start <= end <= 320 and end - start <= 3 and
            2 <= modulus <= 35):
        raise ValueError("invalid finite shard")
    lines = [f"DOMAIN E5BIGSHARDv1 {start} {end} {modulus}"]
    powers = [x ** 5 for x in range(end + 1)]
    total_visits = total_hits = 0
    for e in range(start, end + 1):
        pairs: dict[int, list[tuple[int, int]]] = defaultdict(list)
        for a in range(1, e):
            for b in range(a, e):
                pairs[powers[a] + powers[b]].append((a, b))
        visits = Counter()
        hits = Counter()
        for c in range(1, e):
            for d in range(c, e):
                right = powers[c] + powers[d]
                target = powers[e] - right
                if target <= 0:
                    continue
                key = tuple(sorted((target % modulus, right % modulus)))
                visits[key] += 1
                total_visits += 1
                for a, b in pairs.get(target, []):
                    if b <= c and gcd(a, b, c, d, e) == 1:
                        lines.append(f"CERT E5v1 {a} {b} {c} {d} {e}")
                        hits[key] += 1
                        total_hits += 1
        for lo in range(modulus):
            for hi in range(lo, modulus):
                if (lo + hi) % modulus == powers[e] % modulus:
                    lines.append(f"PART {e} {lo} {hi} {visits[lo, hi]} {hits[lo, hi]}")
    lines.append(f"SHARD {start} {end} {modulus} {total_visits} {total_hits}")
    return ("\n".join(lines) + "\n").encode("ascii")


def atomic(path: Path, content: bytes) -> None:
    tmp = path.with_name(path.name + ".pending")
    with tmp.open("wb") as fh:
        fh.write(content)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def load_canonical(path: Path) -> dict:
    raw = path.read_bytes()
    obj = json.loads(raw)
    if not isinstance(obj, dict) or canonical(obj) != raw:
        raise ValueError(f"noncanonical JSON in {path.name}")
    return obj


def filename(start: int, end: int) -> str:
    return f"e{start:03d}-{end:03d}"


def validate_stream(data: bytes, start: int, end: int, modulus: int,
                    max_bytes: int) -> dict:
    if len(data) > max_bytes or not data.isascii():
        raise ValueError("oversized or non-ASCII native transcript")
    expected = oracle(start, end, modulus)
    if data != expected:
        raise ValueError(f"independent exact oracle disagrees with [{start},{end}]")
    lines = data.decode("ascii").splitlines()
    footer = [natural(v) for v in lines[-1].split(" ")[1:]]
    return {"visits": footer[3], "witnesses": footer[4],
            "bytes": len(data), "sha256": digest(data),
            "certificate_rows": [line for line in lines if line.startswith("CERT ")]}


def expected_receipt(plan_hash: str, plan: dict, start: int, end: int,
                     observed: dict) -> dict:
    return {
        "schema": RECEIPT, "state": "independently_verified",
        "plan_sha256": plan_hash, "source": plan["source"],
        "height_range": [start, end], "modulus": plan["modulus"],
        "transcript_sha256": observed["sha256"],
        "transcript_bytes": observed["bytes"],
        "right_pair_visits": observed["visits"],
        "witnesses": observed["witnesses"],
        "certificate_rows": observed["certificate_rows"],
        "oracle": "independent Python exact full ordered-pair enumeration",
    }


def verify_shard(folder: Path, plan: dict, plan_hash: str,
                 start: int, end: int, max_bytes: int) -> dict:
    name = filename(start, end)
    stream = folder / (name + ".txt")
    receipt = folder / (name + ".receipt.json")
    if not (stream.is_file() and receipt.is_file()):
        raise ValueError(f"missing transcript or verified receipt: {name}")
    measured = validate_stream(stream.read_bytes(), start, end,
                               plan["modulus"], max_bytes)
    want = expected_receipt(plan_hash, plan, start, end, measured)
    if load_canonical(receipt) != want:
        raise ValueError(f"unverified, stale, or tampered receipt: {name}")
    return want


def validate_acceptance(folder: Path, plan: dict, max_bytes: int) -> dict:
    check_plan(plan)
    plan_hash = digest(canonical(plan))
    expected_names = {filename(a, b) for a, b in map(tuple, plan["intervals"])}
    for suffix in (".txt", ".receipt.json"):
        observed_names = {p.name[:-len(suffix)]
                          for p in folder.glob("e*" + suffix)}
        if observed_names != expected_names:
            raise ValueError("extra or missing accepted shard files")
    if (folder / "plan.json").read_bytes() != canonical(plan):
        raise ValueError("plan bytes mutated after publication")
    receipts = [verify_shard(folder, plan, plan_hash, a, b, max_bytes)
                for a, b in map(tuple, plan["intervals"])]
    witnesses = [line for r in receipts for line in r["certificate_rows"]]
    if len(witnesses) != len(set(witnesses)):
        raise ValueError("duplicate witness across disjoint shards")
    return {
        "schema": ACCEPTANCE, "state": "all_declared_heights_independently_replayed",
        "scope": {"min_e": 2, "max_e": plan["last_height"],
                  "modulus": plan["modulus"], "strictly_positive": True,
                  "primitive": True},
        "plan_sha256": plan_hash, "source": plan["source"],
        "shard_receipts": [digest(canonical(r)) for r in receipts],
        "shards": len(receipts),
        "right_pair_visits": sum(r["right_pair_visits"] for r in receipts),
        "certificates": witnesses,
    }


def limits(timeout: int, ram_mib: int, max_bytes: int) -> None:
    resource.setrlimit(resource.RLIMIT_CPU, (timeout * 2, timeout * 2 + 1))
    resource.setrlimit(resource.RLIMIT_AS, (ram_mib * 1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (max_bytes,) * 2)


def compile_binary(destination: Path) -> None:
    deps = ROOT / ".deps/finite-math-kernels/kernel"
    if not deps.is_dir():
        raise ValueError("pinned shared checkout missing; run locked research verification")
    checkout = deps.parent
    actual = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"], cwd=ROOT,
        text=True, timeout=15,
    ).strip()
    if actual != dependency_pin():
        raise ValueError("untrusted finite-math-kernels HEAD: refuses dependency drift")
    dirty = subprocess.check_output(
        ["git", "-C", str(checkout), "status", "--porcelain",
         "--untracked-files=all"], cwd=ROOT, text=True, timeout=15,
    ).strip()
    if dirty:
        raise ValueError("untrusted finite-math-kernels working tree differs from pin")
    subprocess.run(["mojo", "build", "-I", "kernel", "-I", str(deps),
                    "kernel/bigz_shard.mojo", "-o", str(destination)],
                   check=True, cwd=ROOT, timeout=180)


def execute(folder: Path, plan: dict, timeout: int, ram_mib: int,
            max_bytes: int) -> dict:
    check_plan(plan)
    folder.mkdir(parents=True, exist_ok=True)
    plan_path = folder / "plan.json"
    if plan_path.exists():
        if plan_path.read_bytes() != canonical(plan):
            raise ValueError("existing plan has different scope or source")
    else:
        atomic(plan_path, canonical(plan))
    plan_hash = digest(canonical(plan))
    if (folder / "accepted.json").exists():
        existing = load_canonical(folder / "accepted.json")
        if existing != validate_acceptance(folder, plan, max_bytes):
            raise ValueError("previous accepted manifest is stale or corrupted")
    with TemporaryDirectory(prefix="e5-bigz-") as work:
        binary = Path(work) / "bigz-shard"
        compile_binary(binary)
        for a, b in map(tuple, plan["intervals"]):
            name = filename(a, b)
            stream, receipt = folder / (name + ".txt"), folder / (name + ".receipt.json")
            if stream.is_file() and receipt.is_file():
                verify_shard(folder, plan, plan_hash, a, b, max_bytes)
                print(f"REPLAYED {name}", flush=True)
                continue
            if receipt.exists():
                raise ValueError("verified receipt exists without its transcript")
            if stream.exists():
                started = folder / (name + ".attempt.json")
                ticket = load_canonical(started) if started.exists() else None
                if (ticket is None or ticket.get("state") != "started" or
                    ticket.get("plan_sha256") != plan_hash or
                    ticket.get("height_range") != [a, b]):
                    raise ValueError("orphan transcript without scoped attempt")
                measured = validate_stream(stream.read_bytes(), a, b,
                                           plan["modulus"], max_bytes)
                atomic(receipt, canonical(expected_receipt(
                    plan_hash, plan, a, b, measured)))
                started.unlink()
                print(f"RECOVERED VERIFIED {name}", flush=True)
                continue
            attempt = folder / (name + ".attempt.json")
            previous = load_canonical(attempt) if attempt.exists() else None
            if previous is not None and previous.get("plan_sha256") != plan_hash:
                raise ValueError("stale attempt cannot be retried")
            ticket = (previous["ticket"] + 1) if previous else 1
            if ticket > 3:
                raise ValueError("per-shard retry budget exhausted")
            abort = folder / (name + ".abort.json")
            atomic(attempt, canonical({"state": "started", "ticket": ticket,
                                       "plan_sha256": plan_hash,
                                       "height_range": [a, b]}))
            staged = folder / (name + ".running")
            started = monotonic_ns()
            try:
                with staged.open("wb") as output:
                    subprocess.run([str(binary), str(a), str(b),
                                    str(plan["modulus"])], stdout=output,
                                   check=True, timeout=timeout, cwd=ROOT,
                                   preexec_fn=lambda: limits(timeout, ram_mib, max_bytes))
                measurement = validate_stream(staged.read_bytes(), a, b,
                                              plan["modulus"], max_bytes)
                valid = expected_receipt(plan_hash, plan, a, b, measurement)
                # Write accepted transcript first, receipt only after validation.
                os.replace(staged, stream)
                atomic(receipt, canonical(valid))
                attempt.unlink()
                if abort.exists():
                    abort.unlink()
                print(f"VERIFIED {name} visits={measurement['visits']} "
                      f"certs={measurement['witnesses']} "
                      f"elapsed_ms={(monotonic_ns()-started)//1000000}", flush=True)
            except Exception as error:
                if staged.exists():
                    staged.unlink()
                # Aborted attempts are recorded, never promoted to verified.
                atomic(abort, canonical({
                    "state": "aborted", "ticket": ticket,
                    "plan_sha256": plan_hash, "height_range": [a, b],
                    "error_kind": type(error).__name__,
                }))
                # The monotonic attempt ticket survives for a bounded retry.
                raise
    manifest = validate_acceptance(folder, plan, max_bytes)
    atomic(folder / "accepted.json", canonical(manifest))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["plan", "execute", "verify"])
    parser.add_argument("--bound", default="16")
    parser.add_argument("--width", default="4")
    parser.add_argument("--modulus", default="35")
    parser.add_argument("--timeout", default="60")
    parser.add_argument("--ram-mib", default="4096")
    parser.add_argument("--max-bytes", default="1048576")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    bound, width, modulus = map(natural, [args.bound, args.width, args.modulus])
    timeout, ram_mib, max_bytes = map(natural,
                                      [args.timeout, args.ram_mib, args.max_bytes])
    valid_domain(bound, width, modulus)
    if not (5 <= timeout <= 300 and 512 <= ram_mib <= 8192 and
            4096 <= max_bytes <= 1048576):
        raise ValueError("unsupported finite resource budget")
    folder = args.output.resolve()
    if args.action == "plan":
        plan = make_plan(bound, width, modulus)
        print(canonical(plan).decode("ascii"), end="")
        return
    if args.action == "execute":
        result = execute(folder, make_plan(bound, width, modulus),
                         timeout, ram_mib, max_bytes)
    else:
        plan = load_canonical(folder / "plan.json")
        result = validate_acceptance(folder, plan, max_bytes)
        if (folder / "accepted.json").read_bytes() != canonical(result):
            raise ValueError("acceptance record does not match independent replay")
    print(f"ACCEPTED exactly heights 2..{result['scope']['max_e']}, "
          f"{result['shards']} shards, {result['right_pair_visits']} visits, "
          f"{len(result['certificates'])} witnesses.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        raise SystemExit(1)
