"""Unfiltered exact oracle checks, signed native calibration, and receipt corruption."""
from __future__ import annotations
from collections import Counter
import json
from math import gcd
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from search_novel_stripes import ROOT, canonical, independent_oracle, plan, sha, source_identity
from search_discovery_frontier import COLUMNS, frontier_plan, verify_cell


def refused(f):
    try:
        f()
    except (ValueError, OSError):
        return
    raise AssertionError("corrupt evidence accepted")


def brute(e, delta, cap, amin, sign):
    d=e-delta
    return [(a,b,c,d,e) for c in range(1,d+1) for m in range(amin,min(c,cap)+1)
            for a in [m if sign=="positive" else -m] for b in range(m,c+1)
            if a**5+b**5+c**5+d**5==e**5 and gcd(a,b,c,d,e)==1]


def main():
    cells=frontier_plan()
    assert len(cells)==11 and sum(x["pairs_upper_budget"] for x in cells)==176372608
    for e in range(5,20):
        for delta in range(1,e):
            for sign in ("positive","negative"):
                expected=brute(e,delta,6,2,sign)
                try:
                    scope=plan(e,delta,6,4096,2,sign)
                except ValueError:
                    assert not expected
                    continue
                transcript=independent_oracle(e,delta,6,scope["c_min"],scope["c_max"],scope)
                actual=[tuple(map(int,line.split()[2:])) for line in transcript.splitlines() if line.startswith("CERT ")]
                assert actual==expected,(e,delta,sign,actual,expected)
    for amin,cap,sign in [(0,64,"positive"),(65,64,"positive"),(1,257,"positive"),(1,64,"other")]:
        refused(lambda:plan(2760001,1,cap,4096,amin,sign))
    scope=plan(144,11,64,4096,28,"positive")
    # Complete finite synthetic fixture with exact arithmetic and explicit fake time.
    with TemporaryDirectory() as tmp:
        folder=Path(tmp); totals=Counter(); stripes=[]; resources=[]
        for lo,hi in scope["ranges"]:
            text=independent_oracle(144,11,64,lo,hi,scope).encode("ascii")
            stem=folder/f"c{lo:06d}-{hi:06d}"
            stem.with_suffix(".txt").write_bytes(text)
            timing=b"0.01 0.00 0.00 1\n";stem.with_suffix(".time").write_bytes(timing)
            stripes.append({"interval":[lo,hi],"transcript_sha256":sha(text)})
            resources.append({"interval":[lo,hi],"native_wall_ns":1,"python_replay_wall_ns":1,"gnu_wall_seconds":"0.01","gnu_user_seconds":"0.00","gnu_system_seconds":"0.00","max_rss_kib":1,"time_file_sha256":sha(timing)})
            for k,n in zip(COLUMNS,map(int,text.decode().splitlines()[-1].split()[1:])):totals[k]+=n
        record={"schema":"E5-DELTA-STRIPE-ACCEPTANCE-v2","scope":scope,"source":source_identity(),"per_stripe":stripes,"resources":resources,"totals":dict(totals),"witnesses":[]}
        receipt=folder/"accepted.json"
        def write():receipt.write_bytes(canonical(record))
        write();verify_cell(folder,scope)
        for key in ("trials","exact_lookups","residue_or_nonpositive_rejects","primitive_witnesses"):
            record["totals"][key]+=1;write();refused(lambda:verify_cell(folder,scope));record["totals"][key]-=1
        old=record["source"];record["source"]={"fake":"source"};write();refused(lambda:verify_cell(folder,scope));record["source"]=old
        # A self-consistently rehashed false transcript still fails arithmetic replay.
        lo,hi=scope["ranges"][0];path=folder/f"c{lo:06d}-{hi:06d}.txt";original=path.read_bytes()
        bad=original.replace(b"SUMMARY",b"SUMMARX");path.write_bytes(bad);record["per_stripe"][0]["transcript_sha256"]=sha(bad);write();refused(lambda:verify_cell(folder,scope))
        path.write_bytes(original);record["per_stripe"][0]["transcript_sha256"]=sha(original);write()
        (folder/"extra.txt").write_text("foreign");refused(lambda:verify_cell(folder,scope))
    if "--python-only" not in sys.argv:
        samples=[(144,11,64,27,"positive",105,113,"CERT E5v1 27 84 110 133 144"),
                 (14132,64,256,220,"negative",6237,6237,"CERT E5v1 -220 5027 6237 14068 14132"),
                 (144,11,64,28,"positive",105,113,None)]
        for e,d,A,amin,sign,lo,hi,cert in samples:
            scope=plan(e,d,A,4096,amin,sign)
            cmd=["bash","scripts/run_mojo.sh","kernel/near_cancellation_stripe.mojo",*map(str,(e,d,A,lo,hi,amin,int(sign=="negative")))]
            r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=120)
            assert r.returncode==0,r.stderr
            assert r.stdout==independent_oracle(e,d,A,lo,hi,scope)
            certs=[x for x in r.stdout.splitlines() if x.startswith("CERT ")]
            assert certs==([cert] if cert else [])
        # Native guards, using otherwise valid c bounds.
        for amin,cap,negative in [(0,64,0),(65,64,0),(1,257,0),(1,64,2)]:
            r=subprocess.run(["bash","scripts/run_mojo.sh","kernel/near_cancellation_stripe.mojo",*map(str,(144,11,cap,105,113,amin,negative))],cwd=ROOT,capture_output=True,text=True,timeout=120)
            assert r.returncode!=0
    print("Frontier unfiltered exhaustive small-domain oracle, finite budgets, source/count/transcript tamper refusal, and requested native calibrations passed.")

if __name__=="__main__":main()
