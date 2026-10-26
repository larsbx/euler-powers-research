"""Independent finite (e,delta) grid planning and fail-closed evidence intake."""
from __future__ import annotations

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from search_discovery_grid import grid_plan,verify_child
from search_novel_stripes import canonical,sha


def refused(f):
    try:
        f()
    except (ValueError,OSError):
        return
    raise AssertionError("unsafe grid evidence accepted")


def main():
    plans=grid_plan(2760001,2760003,1,3,64,4096)
    assert len(plans)==9
    assert [(p["e"],p["delta"]) for p in plans]==[
        (e,d) for e in range(2760001,2760004) for d in range(1,4)
    ]
    assert all(p["c_min"]<=p["c_max"]<=p["d"] for p in plans)
    assert all(p["ranges"][0][0]==p["c_min"] and
               p["ranges"][-1][1]==p["c_max"] for p in plans)
    for p in plans:
        for (_,end),(next_start,_) in zip(p["ranges"],p["ranges"][1:]):
            assert next_start==end+1
    for args in [
        (2760000,2760003,1,3,64,4096),
        (2760001,2760010,1,3,64,4096),
        (2760001,2760003,1,1025,64,4096),
        (2760001,2760003,1,3,1025,4096),
        (2760001,2760003,1,3,64,4097),
    ]:
        refused(lambda args=args:grid_plan(*args))

    with TemporaryDirectory() as t:
        folder=Path(t)
        scope=plans[0]
        pairs=scope["ranges"]
        fake={
            "schema":"E5-DELTA-STRIPE-ACCEPTANCE-v1",
            "scope":scope,"source":{"test":"synthetic-only"},
            "totals":{"c_values":scope["c_max"]-scope["c_min"]+1,
                      "primitive_witnesses":0,
                      "trials":1,"exact_lookups":0},
            "witnesses":[],
            "per_stripe":[]
        }
        for lo,hi in pairs:
            payload=f"SYNTHETIC {lo} {hi}\n".encode("ascii")
            name=f"c{lo:06d}-{hi:06d}.txt"
            (folder/name).write_bytes(payload)
            fake["per_stripe"].append({
                "interval":[lo,hi],"transcript_sha256":sha(payload)
            })
        (folder/"accepted.json").write_bytes(canonical(fake))
        assert verify_child(folder,scope)==fake
        first=pairs[0]
        path=folder/f"c{first[0]:06d}-{first[1]:06d}.txt"
        path.write_bytes(b"TAMPERED\n")
        refused(lambda:verify_child(folder,scope))
        path.write_bytes(f"SYNTHETIC {first[0]} {first[1]}\n".encode("ascii"))
        wrong=dict(scope)
        wrong["e"]=scope["e"]+1
        refused(lambda:verify_child(folder,wrong))
        fake["per_stripe"]=fake["per_stripe"][:-1]
        (folder/"accepted.json").write_bytes(canonical(fake))
        refused(lambda:verify_child(folder,scope))
    print("E5 novelty grid: complete fixed-parameter planning, exact finite "
          "coverage, and tampered/missing-source receipt refusals passed.")


if __name__=="__main__":
    main()

