"""Unfiltered witnesses, exact root boundaries, native controls, finite P16 scope."""
from pathlib import Path
from math import gcd
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from search_novel_stripes import ROOT, independent_oracle, plan, two_fifth_ceil
from search_discovery_p16 import p16_plan
from test_discovery_frontier import brute


def certs(text):
    return [tuple(map(int,x.split()[2:])) for x in text.splitlines() if x.startswith('CERT ')]


def main():
    cells=p16_plan()
    assert len(cells)==10
    assert sum(c['pairs_upper_budget'] for c in cells)==318981888
    assert all(c['a_min']==257 and c['a_cap']==1024 and c['bound_mode']=='two_term' for c in cells)
    for upper in (0,1,3,9):
        for n in range(-10,2*upper**5+3):
            x=two_fifth_ceil(n,upper)
            assert 0<=x<=upper+1
            if x<=upper:
                assert 2*x**5>=n and (x==0 or 2*(x-1)**5<n)
            else:assert 2*upper**5<n
    for e in range(5,24):
        for d in range(1,e):
            for sign in ('positive','negative'):
                for amin,cap in ((1,4),(2,6)):
                    expected=brute(e,d,cap,amin,sign)
                    try:scope=plan(e,d,cap,4096,amin,sign,True)
                    except ValueError:
                        assert not expected
                        continue
                    assert certs(independent_oracle(e,d,cap,scope['c_min'],scope['c_max'],scope))==expected
                    D=e**5-(e-d)**5
                    for c in range(scope['legacy_c_min'],scope['c_min']):
                        assert ((cap**5 if sign=='positive' else 0)+2*c**5)<D
    if '--python-only' not in sys.argv:
        # Native whole-c calibration at both published positive identities and
        # Scher-Seidl's signed identity; tight bound must retain each witness.
        samples=[(144,11,64,1,'positive',(27,84,110,133,144)),
                 (85359,77,64,1,'positive',(55,3183,28969,85282,85359)),
                 (14132,64,256,1,'negative',(-220,5027,6237,14068,14132)),
                 (144,11,1024,28,'positive',None)]
        for e,d,A,amin,sign,witness in samples:
            scope=plan(e,d,A,4096,amin,sign,True)
            observed=[]
            for lo,hi in scope['ranges']:
                cmd=['bash','scripts/run_mojo.sh','kernel/near_cancellation_stripe.mojo',*map(str,(e,d,A,lo,hi,amin,int(sign=='negative'),1))]
                r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=120)
                assert r.returncode==0,r.stderr
                assert r.stdout==independent_oracle(e,d,A,lo,hi,scope)
                observed.extend(certs(r.stdout))
            assert observed==([witness] if witness else [])
        # An actual new-region stripe exercises a_min=257 and A=1024.
        c=cells[0];lo=c['c_min'];hi=lo+31
        r=subprocess.run(['bash','scripts/run_mojo.sh','kernel/near_cancellation_stripe.mojo',*map(str,(c['e'],c['delta'],1024,lo,hi,257,0,1))],cwd=ROOT,capture_output=True,text=True,timeout=120)
        assert r.returncode==0,r.stderr
        assert r.stdout==independent_oracle(c['e'],c['delta'],1024,lo,hi,c)
    print('P16 exact root inequalities, impossible-prefix checks, unfiltered positive/signed witness comparisons, scope/budget and requested native controls passed.')

if __name__=='__main__':main()
