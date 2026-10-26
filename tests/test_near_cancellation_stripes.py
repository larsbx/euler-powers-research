"""Independent exact calibration of the native high-height Mojo stripe engine."""
from __future__ import annotations

import subprocess

from check_research_kernels import ROOT
from search_novel_stripes import independent_oracle,plan


def main():
    samples = [
        (144,11,64,105,113),
        (85359,77,64,28965,28969),
    ]
    scope=plan(2760001,1,64,4096)
    assert scope["c_min"]>100000 and scope["c_max"]<600000
    samples.append((2760001,1,64,scope["c_min"],scope["c_min"]+31))
    for e,delta,A,lo,hi in samples:
        bounds=plan(e,delta,A,4096)
        assert bounds["c_min"]<=lo<=hi<=bounds["c_max"]
        args=["bash","scripts/run_mojo.sh","kernel/near_cancellation_stripe.mojo",
              str(e),str(delta),str(A),str(lo),str(hi)]
        result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
        assert result.returncode==0,result.stderr+"\n"+result.stdout
        ref=independent_oracle(e,delta,A,lo,hi,bounds)
        assert result.stdout==ref,(e,delta,result.stdout[-400:],ref[-400:])
        certs=[line for line in result.stdout.splitlines() if line.startswith("CERT ")]
        if e==85359:
            assert certs==["CERT E5v1 55 3183 28969 85282 85359"]
        if e==2760001:
            assert not certs
        print(f"Actual native+independent exact check: e={e} delta={delta} "
              f"c={lo}..{hi}, {len(certs)} primitive certificates.")
    for args in [
        ("2760001","1","64","0","1"),
        ("2760001","1","64","1","2"),
        ("2760001","1","65","1","2"),
        ("4000001","1","64","1","2"),
        ("2760001","0","64","1","2"),
    ]:
        result=subprocess.run(["bash","scripts/run_mojo.sh",
            "kernel/near_cancellation_stripe.mojo",*args],
            cwd=ROOT,text=True,capture_output=True)
        assert result.returncode!=0,(args,result.stdout)
    print("High-height stripe finite-domain guards and native exact arithmetic passed.")


if __name__=="__main__":
    main()
