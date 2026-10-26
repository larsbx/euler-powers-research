"""Resource-bounded, nonoverlapping positive/signed frontier; exact receipt replay."""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from time import monotonic_ns

from search_novel_stripes import ROOT, canonical, independent_oracle, plan, sha, source_identity

PARAMETERS = (
    [(d, 1, 256, "positive") for d in (4, 8, 16, 64, 256)]
    + [(d, 65, 256, "positive") for d in (1, 2, 3)]
    + [(d, 1, 256, "negative") for d in (4, 16, 64)]
)
COLUMNS = ("c_values", "trials", "residue_or_nonpositive_rejects", "exact_lookups", "primitive_witnesses")


def frontier_plan():
    cells = [plan(2760001, d, hi, 4096, lo, sign) for d, lo, hi, sign in PARAMETERS]
    # Reviewed total work ceiling and explicit disjointness from the P14 region.
    if len(cells) > 12 or sum(c["pairs_upper_budget"] for c in cells) > 180_000_000:
        raise ValueError("frontier exceeds reviewed finite work budget")
    for i, c in enumerate(cells):
        if c["sign"] == "positive" and c["delta"] <= 3 and c["a_min"] <= 64:
            raise ValueError("frontier repeats completed P14 positive region")
        for other in cells[:i]:
            if (c["e"], c["delta"], c["sign"]) == (other["e"], other["delta"], other["sign"]):
                if max(c["a_min"], other["a_min"]) <= min(c["a_cap"], other["a_cap"]):
                    raise ValueError("overlapping frontier cells")
    return cells


def cell_id(c):
    return f"e{c['e']}-d{c['delta']}-{c['sign']}-a{c['a_min']}-{c['a_cap']}"


def verify_cell(folder: Path, scope: dict, replay: bool = True):
    payload = (folder / "accepted.json").read_bytes()
    r = json.loads(payload)
    schema = ("E5-DELTA-STRIPE-ACCEPTANCE-v3" if scope.get("bound_mode") == "two_term" else
              "E5-DELTA-STRIPE-ACCEPTANCE-v1" if scope["a_min"] == 1 and scope["sign"] == "positive"
              else "E5-DELTA-STRIPE-ACCEPTANCE-v2")
    if canonical(r) != payload or r["schema"] != schema or r["scope"] != scope:
        raise ValueError("foreign/noncanonical/incomplete scope receipt")
    if r["source"] != source_identity():
        raise ValueError("receipt does not match actual pinned sources and run")
    ranges = scope["ranges"]
    if [p["interval"] for p in r["per_stripe"]] != ranges or [p["interval"] for p in r["resources"]] != ranges:
        raise ValueError("missing/duplicate/reordered stripes or resource records")
    names = {"accepted.json"} | {f"c{lo:06d}-{hi:06d}.{ext}" for lo, hi in ranges for ext in ("txt", "time")}
    if {p.name for p in folder.iterdir()} != names:
        raise ValueError("extra/missing frontier evidence")
    totals = Counter()
    witnesses = []
    registry = json.loads((ROOT / "data/literature/known_primitive_e5_2026-10-26.json").read_text())
    known = {(*x["summands"], x["target"]):x["id"] for x in registry["records"]}
    for stripe, resource in zip(r["per_stripe"], r["resources"]):
        lo, hi = stripe["interval"]
        stem = folder / f"c{lo:06d}-{hi:06d}"
        text = stem.with_suffix(".txt").read_bytes()
        timing = stem.with_suffix(".time").read_bytes()
        if sha(text) != stripe["transcript_sha256"] or sha(timing) != resource["time_file_sha256"]:
            raise ValueError("modified native transcript or resource measurement")
        wall, user, system, rss = timing.decode("ascii").strip().split()
        if (wall, user, system, int(rss)) != (resource["gnu_wall_seconds"], resource["gnu_user_seconds"], resource["gnu_system_seconds"], resource["max_rss_kib"]):
            raise ValueError("resource report disagrees with raw GNU time")
        if any(float(x) < 0 for x in (wall, user, system)) or int(rss) <= 0 or min(resource["native_wall_ns"],resource["python_replay_wall_ns"]) <= 0:
            raise ValueError("invalid resource measurement")
        if replay:
            exact = independent_oracle(scope["e"], scope["delta"], scope["a_cap"], lo, hi, scope).encode("ascii")
            if text != exact:
                raise ValueError("transcript fails independent exact arithmetic replay")
        lines = text.decode("ascii").splitlines()
        row = list(map(int, lines[-1].split()[1:]))
        if lines[-1].split()[0] != "SUMMARY" or len(row) != 5 or row[0] != hi-lo+1 or row[1] != row[2]+row[3]:
            raise ValueError("invalid finite count certificate")
        for k, n in zip(COLUMNS, row):
            totals[k] += n
        for line in lines:
            if line.startswith("CERT E5v1 "):
                terms = tuple(map(int, line.split()[2:]))
                from math import gcd
                if len(terms)!=5 or gcd(*terms)!=1 or sum(x**5 for x in terms[:4]) != terms[4]**5:
                    raise ValueError("invalid exact primitive identity")
                witnesses.append({"tuple":list(terms),"known_id":known.get(terms),"novelty":"known" if terms in known else "candidate_requires_fresh_literature_review"})
    expected_trials = sum(max(0,min(c,scope["a_cap"])-scope["a_min"]+1) for c in range(scope["c_min"],scope["c_max"]+1))
    if dict(totals) != r["totals"] or totals["trials"] != expected_trials or totals["c_values"] != scope["c_max"]-scope["c_min"]+1 or witnesses != r["witnesses"] or totals["primitive_witnesses"] != len(witnesses):
        raise ValueError("coverage/count/witness mismatch")
    return r


def bounded_cell(command, timeout):
    # One process group includes the controller, time, bash and native Mojo.
    # Kill the entire group on a cell timeout; partial output is never accepted.
    p = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
    try:
        stdout, stderr = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        p.communicate()
        raise
    if p.returncode:
        raise RuntimeError(stderr + stdout[-2000:])
    return stdout


def main(cells=None, receipt_name="accepted-frontier.json", controller_path=None,
         schema="E5-DISCOVERY-FRONTIER-v1", extra=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    cells = frontier_plan() if cells is None else cells
    output = args.output.resolve()
    if not args.verify:
        output.mkdir(parents=True, exist_ok=False)
        for c in cells:
            destination = output/cell_id(c)
            command = [sys.executable, "tools/search_novel_stripes.py", "--e", str(c["e"]), "--delta", str(c["delta"]), "--a-min", str(c["a_min"]), "--a-cap", str(c["a_cap"]), "--sign", c["sign"], "--timeout", "120", "--output", str(destination)]
            if c.get("bound_mode") == "two_term":
                command.append("--tight-bounds")
            started = monotonic_ns()
            logs = bounded_cell(command, 600)
            (output/(cell_id(c)+".log")).write_text(logs, encoding="ascii")
            # The child has just replayed every native byte. Fresh verification
            # below rechecks hashes, scope, totals and source identity.
            r = verify_cell(destination, c, replay=False)
            print(f"FRONTIER VERIFIED {cell_id(c)}: {r['totals']}, wall_ms={(monotonic_ns()-started)//1000000}", flush=True)
    rows = []
    for c in cells:
        folder = output/cell_id(c)
        r = verify_cell(folder, c, replay=args.verify)
        rows.append({"cell":cell_id(c),"scope":c,"receipt_sha256":sha((folder/"accepted.json").read_bytes()),"totals":r["totals"],"witnesses":r["witnesses"],"native_wall_ns":sum(x["native_wall_ns"] for x in r["resources"]),"python_replay_wall_ns":sum(x["python_replay_wall_ns"] for x in r["resources"]),"max_native_rss_kib":max(x["max_rss_kib"] for x in r["resources"])})
    record = {"schema":schema,"source":source_identity(),"controller_sha256":sha(Path(controller_path or __file__).read_bytes()),"cells":rows,"total_trials":sum(x["totals"]["trials"] for x in rows),"total_exact_lookups":sum(x["totals"]["exact_lookups"] for x in rows),"witnesses":[w for x in rows for w in x["witnesses"]],"meaning":"complete only for declared cells, signed first term with abs(a)<=b<=c<=d<e; no global nonexistence claim"}
    if extra is not None:
        record.update(extra)
        record["receipt_verifier_sha256"] = sha(Path(__file__).read_bytes())
    target = output/receipt_name
    if args.verify:
        if target.read_bytes() != canonical(record):
            raise ValueError("aggregate differs from independently replayed receipts")
    else:
        target.write_bytes(canonical(record))
    print(f"FRONTIER ACCEPTED: {len(rows)} cells, {record['total_trials']} trials, {record['total_exact_lookups']} exact lookups, {len(record['witnesses'])} witnesses",flush=True)


if __name__ == "__main__":
    main()
