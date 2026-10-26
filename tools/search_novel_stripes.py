"""Deterministic, fully replayed E5 near-cancellation (e,delta,a-cap) stripes.

Runs the REAL Mojo BigZ code. A different Python exact hash-power oracle
reconstructs every trial, rejection, lookup, and positive witness.
Accepted coverage is only the fixed (e,delta,a<=A) c-domain, never all
values of delta, a or e. Published large-search claims aren't reproduced.

Example:
 pixi run --locked python tools/search_novel_stripes.py \\
   --e 2760001 --delta 1 --a-cap 64 --output benchmarks/results/discovery
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from math import gcd
import os
from pathlib import Path
import re
import subprocess
import sys
from time import monotonic_ns

ROOT = Path(__file__).resolve().parents[1]
KNOWN = ROOT / "data/literature/known_primitive_e5_2026-10-26.json"
PATTERN = re.compile(r"0|[1-9][0-9]*\Z", re.ASCII)
SCHEMA = "E5-DELTA-STRIPE-ACCEPTANCE-v1"


def natural(arg: str) -> int:
    if not PATTERN.fullmatch(arg):
        raise ValueError(f"noncanonical integer {arg!r}")
    return int(arg)


def fifth_floor(n: int, upper: int) -> int:
    lo, hi = 0, upper + 1
    while lo + 1 < hi:
        mid = lo + (hi-lo)//2
        if mid**5 <= n:
            lo = mid
        else:
            hi = mid
    return lo


def three_fifth_ceil(n: int, upper: int) -> int:
    lo, hi = 0, upper + 1
    while lo < hi:
        mid = lo + (hi-lo)//2
        if 3*mid**5 < n:
            lo = mid + 1
        else:
            hi = mid
    return lo


def plan(e: int, delta: int, a_cap: int, width: int) -> dict:
    if not (5 <= e <= 4000000 and 1 <= delta <= 256 and delta < e and
            1 <= a_cap <= 64 and 1 <= width <= 4096):
        raise ValueError("unsupported high-height finite search domain")
    d = e-delta
    difference = e**5-d**5
    c_min = three_fifth_ceil(difference, d)
    c_max = fifth_floor(difference, d)
    if not (1 <= c_min <= c_max <= d and c_max <= 600000):
        raise ValueError("empty/out-of-policy exact c-bound range")
    ranges = [[x, min(x+width-1, c_max)]
              for x in range(c_min, c_max+1, width)]
    return {"e":e, "delta":delta, "a_cap":a_cap, "d":d,
            "c_min":c_min, "c_max":c_max, "c_width":width,
            "ranges":ranges, "pairs_upper_budget":a_cap*(c_max-c_min+1)}


def independent_oracle(e: int, delta: int, a_cap: int,
                       lo: int, hi: int, bounds: dict) -> str:
    """Exact Python full power-index hash lookup, unlike Mojo binary search."""
    assert bounds["c_min"] <= lo <= hi <= bounds["c_max"]
    D = e**5-(e-delta)**5
    powers = [x**5 for x in range(hi+1)]
    by_power = {value:x for x,value in enumerate(powers)}
    # Full b-residue prefix is a *necessary* modular prefilter only.
    seen = set(pow(b, 5, 99000) for b in range(1, lo))
    lines = [f"DOMAIN E5STRIPEv1 {e} {delta} {a_cap} {lo} {hi}",
             f"BOUNDS {bounds['c_min']} {bounds['c_max']} {e-delta}"]
    trials = rejected = lookups = hits = 0
    for c in range(lo,hi+1):
        seen.add(powers[c] % 99000)
        for a in range(1,min(c,a_cap)+1):
            trials += 1
            complement = D-powers[c]-powers[a]
            if complement <= 0 or complement%99000 not in seen:
                rejected += 1
                continue
            lookups += 1
            b = by_power.get(complement)
            if b is not None and a <= b <= c:
                if gcd(a,b,c,e-delta,e)==1:
                    assert powers[a]+powers[b]+powers[c]+(e-delta)**5==e**5
                    hits += 1
                    lines.append(f"CERT E5v1 {a} {b} {c} {e-delta} {e}")
    lines.append(f"SUMMARY {hi-lo+1} {trials} {rejected} {lookups} {hits}")
    return "\n".join(lines)+"\n"


def canonical(value: object) -> bytes:
    return (json.dumps(value,sort_keys=True,separators=(",",":"))+"\n").encode("ascii")


def sha(data: bytes) -> str:
    return sha256(data).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--e",required=True)
    ap.add_argument("--delta",required=True)
    ap.add_argument("--a-cap",required=True)
    ap.add_argument("--c-width",default="4096")
    ap.add_argument("--timeout",default="120")
    ap.add_argument("--output",required=True,type=Path)
    args = ap.parse_args()
    e,delta,a_cap,width,timeout = (
        natural(z) for z in (args.e,args.delta,args.a_cap,args.c_width,args.timeout)
    )
    if not 5 <= timeout <= 300:
        raise ValueError("bounded per-stripe wall time required")
    scope = plan(e,delta,a_cap,width)
    known_registry = json.loads(KNOWN.read_text(encoding="utf-8"))
    known = {
        (*r["summands"],r["target"]):r["id"]
        for r in known_registry["records"]
        if r["domain"]=="strictly_positive"
    }
    actual_covered = []
    records = []
    totals = Counter()
    outset = args.output.resolve()
    # Each accepted corpus is immutable. Exclusive directory creation
    # prevents a rerun, changed scope or overlapping worker from
    # overwriting even one pre-existing verified transcript.
    # After an interruption use a fresh directory; never merge partial
    # foreign evidence into an accepted scientific run.
    outset.mkdir(parents=True,exist_ok=False)
    started = monotonic_ns()
    for lo,hi in scope["ranges"]:
        command = ["bash","scripts/run_mojo.sh",
                   "kernel/near_cancellation_stripe.mojo",
                   str(e),str(delta),str(a_cap),str(lo),str(hi)]
        native = subprocess.run(command,cwd=ROOT,text=True,capture_output=True,
                                timeout=timeout,check=False)
        if native.returncode != 0:
            raise RuntimeError(f"native failed [{lo},{hi}]: {native.stderr}")
        expected = independent_oracle(e,delta,a_cap,lo,hi,scope)
        if native.stdout != expected:
            raise AssertionError(f"Mojo disagrees with independent exact oracle at [{lo},{hi}]")
        lines = native.stdout.splitlines()
        row = tuple(map(int,lines[-1].split(" ")[1:]))
        if len(row)!=5 or row[0]!=hi-lo+1 or row[1]!=row[2]+row[3]:
            raise ValueError("uncertified stripe SUMMARY")
        certificate_lines = [r for r in lines if r.startswith("CERT E5v1 ")]
        if row[-1]!=len(certificate_lines):
            raise ValueError("native witness count mismatch")
        for cert in certificate_lines:
            terms = tuple(map(int,cert.split(" ")[2:]))
            if (len(terms)!=5 or not 1<=terms[0]<=terms[1]<=terms[2]<=terms[3]<terms[4]
                    or gcd(*terms)!=1
                    or sum(x**5 for x in terms[:4])!=terms[4]**5):
                raise ValueError("unsupported/incorrect witness identity")
            records.append({"tuple":list(terms),"known_id":known.get(terms),
                            "novelty":"known" if terms in known else "candidate_requires_fresh_literature_review"})
        for col,value in zip(("c_values","trials","residue_or_nonpositive_rejects",
                              "exact_lookups","primitive_witnesses"),row):
            totals[col]+=value
        name=f"c{lo:06d}-{hi:06d}"
        transcript = outset/(name+".txt")
        payload=native.stdout.encode("ascii")
        transcript.write_bytes(payload)
        actual_covered.append([lo,hi])
        print(f"VERIFIED e={e},delta={delta},a<={a_cap}, c={lo}..{hi}: "
              f"{row[1]} trials, {row[3]} exact lookups, {row[4]} certs",flush=True)
    if actual_covered!=scope["ranges"] or totals["c_values"]!=scope["c_max"]-scope["c_min"]+1:
        raise ValueError("coverage has a gap, duplication or missing tail")
    if totals["trials"]!=sum(sum(min(c,a_cap) for c in range(lo,hi+1))
                              for lo,hi in scope["ranges"]):
        raise ValueError("trials do not cover finite (a,c) domain")
    source = {
        "mojo_stripe_sha256":sha((ROOT/"kernel/near_cancellation_stripe.mojo").read_bytes()),
        "mojo_bridge_sha256":sha((ROOT/"kernel/near_cancellation.mojo").read_bytes()),
        "exact_math_sha256":sha((ROOT/"kernel/euler_exact.mojo").read_bytes()),
        "python_verifier_sha256":sha(Path(__file__).read_bytes()),
        "known_registry_sha256":sha(KNOWN.read_bytes()),
    }
    manifest = {"schema":SCHEMA,"scope":scope,
                "source":source,"totals":dict(sorted(totals.items())),
                "witnesses":records,
                "per_stripe":[
                    {"interval":interval,
                     "transcript_sha256":sha((outset/(f"c{interval[0]:06d}-{interval[1]:06d}.txt")).read_bytes())}
                    for interval in actual_covered],
                "meaning":"complete for exactly e,delta,a<=A and every mathematically admissible c; NOT a complete e search or novel-solution declaration"}
    output=outset/"accepted.json"
    temp=outset/"accepted.json.pending"
    with temp.open("wb") as f:
        f.write(canonical(manifest))
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp,output)
    print(f"ACCEPTED E5STRIPE e={e} delta={delta} a<={a_cap}: "
          f"{len(actual_covered)} stripes, {totals['trials']} trials, "
          f"{totals['exact_lookups']} exact lookups, "
          f"{len(records)} primitive positive certificates, "
          f"elapsed_ms={(monotonic_ns()-started)//1000000}.",
          flush=True)


if __name__=="__main__":
    try:
        main()
    except (ValueError,AssertionError,OSError,subprocess.SubprocessError,RuntimeError) as err:
        print(f"REFUSED E5STRIPE: {err}",file=sys.stderr)
        raise SystemExit(1)
