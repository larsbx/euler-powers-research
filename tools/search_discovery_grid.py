"""Finite, gap-free (e,delta) discovery grid of actual native Mojo stripes.

Each grid cell independently executes and verifies ALL exact c values for
one target e, delta=e-d, and 1<=a<=A. Grid acceptance asserts that
every declared (e,delta) cell was completed, not that every delta at
each e or every possible small summand was searched.

New scientific artifacts use exclusive directory creation and are never
overwritten. No background execution, no unsigned-worker authority.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
from time import monotonic_ns

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"tools"))
from search_novel_stripes import (
    natural, plan, sha, canonical
)

REGISTRY = ROOT/"data/literature/known_primitive_e5_2026-10-26.json"


def grid_plan(e_start: int, e_end: int, delta_start: int,
              delta_end: int, a_cap: int, width: int) -> list[dict]:
    if (e_start < 2760001 or e_end > 4000000 or
        e_end < e_start or e_end-e_start > 7 or
        delta_start < 1 or delta_end > 256 or
        delta_end < delta_start or delta_end-delta_start > 7 or
        (e_end-e_start+1)*(delta_end-delta_start+1) > 24):
        raise ValueError("grid scope exceeds declared research budget")
    return [plan(e,delta,a_cap,width)
            for e in range(e_start,e_end+1)
            for delta in range(delta_start,delta_end+1)]


def verify_child(folder: Path, expected: dict) -> dict:
    accepted = folder/"accepted.json"
    if not accepted.is_file():
        raise ValueError("missing child acceptance")
    data=accepted.read_bytes()
    record=json.loads(data)
    if canonical(record)!=data or record.get("schema")!="E5-DELTA-STRIPE-ACCEPTANCE-v1":
        raise ValueError("noncanonical child result")
    if record.get("scope")!=expected:
        raise ValueError("foreign/partial child scope")
    if len(record.get("per_stripe",[]))!=len(expected["ranges"]):
        raise ValueError("missing/extra child stripe")
    expected_names={
        f"c{lo:06d}-{hi:06d}.txt" for lo,hi in expected["ranges"]
    }
    if {p.name for p in folder.glob("c*.txt")}!=expected_names:
        raise ValueError("extra, missing or out-of-plan native transcripts")
    for observed, interval in zip(record["per_stripe"],expected["ranges"]):
        if observed["interval"]!=interval:
            raise ValueError("gap, repeated or out-of-order child stripe")
        lo,hi=interval
        transcript=folder/f"c{lo:06d}-{hi:06d}.txt"
        if not transcript.is_file() or sha(transcript.read_bytes())!=observed["transcript_sha256"]:
            raise ValueError("missing or tampered native Mojo transcript")
    if record["totals"]["c_values"]!=expected["c_max"]-expected["c_min"]+1:
        raise ValueError("incomplete c coverage")
    if record["totals"]["primitive_witnesses"]!=len(record["witnesses"]):
        raise ValueError("unverified child witness total")
    return record


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--e-start",required=True)
    p.add_argument("--e-end",required=True)
    p.add_argument("--delta-start",required=True)
    p.add_argument("--delta-end",required=True)
    p.add_argument("--a-cap",default="64")
    p.add_argument("--c-width",default="4096")
    p.add_argument("--timeout",default="240")
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    es,ee,ds,de,a,width,timeout=(
        natural(s) for s in (args.e_start,args.e_end,args.delta_start,
                              args.delta_end,args.a_cap,args.c_width,args.timeout)
    )
    if not 30<=timeout<=600:
        raise ValueError("invalid finite per-cell wall budget")
    cells=grid_plan(es,ee,ds,de,a,width)
    output=args.output.resolve()
    output.mkdir(parents=True,exist_ok=False)
    seen=set()
    cell_rows=[]
    exact_candidates=[]
    total_trials=0
    total_lookups=0
    started=monotonic_ns()
    common_source=None
    for scope in cells:
        e=scope["e"]
        delta=scope["delta"]
        cell_id=f"e{e:07d}-delta{delta:03d}-a{a}"
        if cell_id in seen:
            raise ValueError("duplicate grid cell")
        seen.add(cell_id)
        destination=output/cell_id
        runner=[
            sys.executable,"tools/search_novel_stripes.py",
            "--e",str(e),"--delta",str(delta),
            "--a-cap",str(a),"--c-width",str(width),
            "--timeout","120",
            "--output",str(destination)
        ]
        process=subprocess.run(runner,cwd=ROOT,check=False,
                               capture_output=True,text=True,timeout=timeout)
        if process.returncode!=0:
            raise RuntimeError(f"unverified cell {cell_id}: {process.stderr}")
        accepted=verify_child(destination,scope)
        source=accepted["source"]
        if common_source is None:
            common_source=source
        elif common_source!=source:
            raise ValueError("inconsistent source identity across grid cells")
        trials=accepted["totals"]["trials"]
        lookups=accepted["totals"]["exact_lookups"]
        total_trials+=trials
        total_lookups+=lookups
        exact_candidates.extend(accepted["witnesses"])
        cell_rows.append({
            "e":e,"delta":delta,"a_cap":a,
            "scope":scope,
            "sha256":sha((destination/"accepted.json").read_bytes()),
            "trials":trials,"exact_lookups":lookups,
            "certificates":accepted["witnesses"]
        })
        print(f"GRID VERIFIED e={e} delta={delta} a<={a}: "
              f"{trials} trials, {lookups} lookups, "
              f"{len(accepted['witnesses'])} certificates",flush=True)
    if len(cell_rows)!=len(cells):
        raise ValueError("incomplete parameter grid")
    signature={
        "schema":"E5-POSTBRAUN-GRID-ACCEPTED-v1",
        "parameters":{"e_start":es,"e_end":ee,"delta_start":ds,
                      "delta_end":de,"a_cap":a,"c_width":width},
        "source":common_source,
        "grid_source_sha256":sha(Path(__file__).read_bytes()),
        "known_registry_sha256":sha(REGISTRY.read_bytes()),
        "cells":cell_rows,
        "total_trials":total_trials,
        "total_exact_lookups":total_lookups,
        "witnesses":exact_candidates,
        "meaning":"complete only for declared (e,delta,a<=A) grid cells and each full admissible c range; not an unrestricted e census"
    }
    (output/"accepted-grid.json").write_bytes(canonical(signature))
    print(f"GRID ACCEPTED e={es}..{ee},delta={ds}..{de},a<={a}: "
          f"{len(cell_rows)} cells, {total_trials} trials, "
          f"{total_lookups} exact lookups, {len(exact_candidates)} certificates, "
          f"elapsed_ms={(monotonic_ns()-started)//1000000}.",flush=True)


if __name__=="__main__":
    try:
        main()
    except (ValueError,AssertionError,OSError,subprocess.SubprocessError,
            RuntimeError) as err:
        print(f"REFUSED E5GRID: {err}",file=sys.stderr)
        raise SystemExit(1)
