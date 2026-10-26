"""Finite signed search with independent nested-integer-square-root replay.

Mojo uses monotone quartic binary search. Python derives each possible r
algebraically using two integer square roots; it never copies that inversion.
The full pair-polynomial modular images are necessary conditions, not CRT
probabilities. A batch receipt gives coverage in this parameterization only.
"""
from __future__ import annotations
import argparse
from functools import lru_cache
from hashlib import sha256
from math import gcd,isqrt
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from primitive_candidates import analyze,canonical,compile_verifier,verify_native,expected_native,verify_dependency,PIN

ROOT=Path(__file__).resolve().parents[1]
SOURCE_PATHS=('discovery/two_gap.mojo','tools/search_two_gap.py',
 'discovery/verify_candidate.mojo','tools/primitive_candidates.py',
 'kernel/euler_exact.mojo','kernel/verify_known.mojo','scripts/run_mojo.sh',
 'data/DISCOVERY_CHARTER.json','data/literature/known_primitive_e5_2026-10-26.json',
 'data/experiments/current.json','data/experiments/index-p19.json',
 '.github/workflows/two-gap.yml','tests/test_two_gap.py','formal/lean/TwoGap.lean',
 'scripts/run_research_cgroup.sh','pixi.toml','pixi.lock')
PREDECESSOR='f55bd4dabafa4d5ec6a7b53257269fdf1232ad34e02e4f07866bae130fa276ab'


def sha(raw):return sha256(raw).hexdigest()
def sources():return {p:sha((ROOT/p).read_bytes()) for p in SOURCE_PATHS}
def validate(cell):
    if type(cell) is not list or len(cell)!=5 or any(type(x) is not int for x in cell):
        raise ValueError('five integer scope fields required')
    e,delta,h,lo,hi=cell
    if not (5<=e<=4000000 and 1<=delta<e and delta<=65536 and
            1<=h<e and h<=65536 and 1<=lo<=hi<e and hi-lo<65536):
        raise ValueError('finite two-gap resource domain exceeded')


@lru_cache(maxsize=128)
def images(h):
    return tuple(frozenset((pow(r+h,5,m)-pow(r,5,m))%m for r in range(m))
                 for m in (99000,41,61))


def reconstruct(q,h):
    """From 16 F/h+4h^4=5((2r+h)^2+h^2)^2; h is positive."""
    if q<=0 or q%h:return None
    w=16*(q//h)+4*h**4
    if w%5:return None
    w//=5;t=isqrt(w)
    if t*t!=w or t<h*h:return None
    v=t-h*h;s=isqrt(v)
    if s*s!=v or (s-h)%2:return None
    r=(s-h)//2
    return r if r>=1 and (r+h)**5-r**5==q else None


def oracle(cell):
    validate(cell);e,delta,h,b_lo,b_hi=cell;d=e-delta;D=e**5-d**5
    image=images(h);counts=[0]*9;hits=[]
    for orientation in range(2):
        for b in range(b_lo,b_hi+1):
            counts[0]+=1
            lo,hi=(b+1,d-h) if orientation==0 else (b,min(d,e-1-h))
            if lo>hi:counts[1]+=1;continue
            # Reconstruct *every* geometrically admissible trial before gates.
            # Thus a false modular rejection is caught independently too.
            q=(D-b**5)*(1 if orientation==0 else -1)
            r=reconstruct(q,h)
            possible=r is not None and lo<=r<=hi
            failed=None
            for j,m in enumerate((99000,41,61)):
                if q%m not in image[j]:failed=j;break
            if failed is not None:
                assert not possible,'modular gate rejected an exact pair'
                counts[2+failed]+=1;continue
            if q<=0:counts[5]+=1;continue
            counts[6]+=1
            if possible:
                u,c=(r,r+h) if orientation==0 else (r+h,r)
                assert b<u<e and b<=c<=d<e and -u**5+b**5+c**5+d**5==e**5
                primitive=int(gcd(u,b,c,d,e)==1)
                counts[7]+=1;counts[8]+=primitive
                hits.append([orientation,b,r,u,c,d,e,primitive])
    assert counts[0]==sum(counts[1:7]) and counts[8]<=counts[7]<=counts[6]
    lines=['DOMAIN E5-TWO-GAP-v1 '+' '.join(map(str,cell))]
    lines+=['HIT '+' '.join(map(str,row)) for row in hits]
    lines+=['SUMMARY '+' '.join(map(str,counts))]
    return ('\n'.join(lines)+'\n').encode('ascii'),counts,hits


def plan():
    # Large positive b bands: none overlap old abs(a)<=b signed ordering,
    # because each represented tuple instead satisfies u>b.
    return [[e,d,h,lo,lo+65535]
      for e in (1956877,1956878,1956879,2760001,3000001)
      for d in (64,665,4096,16384)
      for h in (64,1024,9010,16384)
      for lo in (65537,524289)]


def compile_search(binary):
    verify_dependency()
    subprocess.run(['mojo','build','-I','kernel','-I','.deps/finite-math-kernels/kernel',
                    'discovery/two_gap.mojo','-o',str(binary)],cwd=ROOT,check=True,timeout=300)


def run_cell(binary,cell,folder):
    folder.mkdir(exist_ok=False)
    before=time.monotonic_ns()
    proc=subprocess.run(['/usr/bin/time','-v','-o',str(folder/'resources.txt'),str(binary),*map(str,cell)],
                        capture_output=True,timeout=60,check=True)
    elapsed=time.monotonic_ns()-before
    (folder/'stdout.txt').write_bytes(proc.stdout)
    expected,counts,hits=oracle(cell)
    if proc.stdout!=expected or proc.stderr:raise ValueError('native/Python two-gap disagreement')
    return {'cell':cell,'counts':counts,'hits':hits,'elapsed_process_ns':elapsed,
            'stdout_sha256':sha(proc.stdout),'resources_sha256':sha((folder/'resources.txt').read_bytes())}


def proposal_for(i,row,hit):
    _,b,r,u,c,d,e,primitive=hit
    return {'schema':'E5-CANDIDATE-PROPOSAL-v1','terms':list(map(str,(-u,b,c,d,-e))),
      'method':'exact signed two-gap monotone quartic inversion',
      'provenance':f'cell {i}: {row["cell"]}; actual native stdout SHA256 {row["stdout_sha256"]}'}


def replay(folder):
    receipt=json.loads((folder/'receipt.json').read_bytes())
    if receipt['sources']!=sources() or receipt['finite_math_kernels_pin']!=PIN:
        raise ValueError('foreign source-bound two-gap receipt')
    if receipt['schema']!='E5-TWO-GAP-BATCH-v1' or receipt['cells']!=plan():
        raise ValueError('foreign finite discovery scope')
    total=[0]*9;seen=set()
    for i,row in enumerate(receipt['results']):
        cell=row['cell'];key=tuple(cell)
        if key in seen or cell!=plan()[i]:raise ValueError('duplicate/missing/reordered cell')
        seen.add(key);expected,counts,hits=oracle(cell);child=folder/f'cell-{i:03d}'
        assert row['counts']==counts and row['hits']==hits
        assert (child/'stdout.txt').read_bytes()==expected and row['stdout_sha256']==sha(expected)
        assert row['resources_sha256']==sha((child/'resources.txt').read_bytes())
        total=[x+y for x,y in zip(total,counts)]
    assert len(seen)==len(plan()) and total==receipt['totals']
    cal=receipt['calibration'];expected,counts,hits=oracle([1956878,665,9010,719114,719116])
    assert cal['cell']==[1956878,665,9010,719114,719116] and cal['counts']==counts and cal['hits']==hits
    assert (folder/'calibration/stdout.txt').read_bytes()==expected and cal['stdout_sha256']==sha(expected)
    assert cal['resources_sha256']==sha((folder/'calibration/resources.txt').read_bytes())
    expected_proposals=[(i,proposal_for(i,row,hit)) for i,row in enumerate(receipt['results']) for hit in row['hits']]
    assert len(receipt['candidate_admissions'])==len(expected_proposals)
    for row,(i,prop) in zip(receipt['candidate_admissions'],expected_proposals):
        fresh=analyze(prop);fresh['native_verified']=True
        fresh['remaining_obligations']=[x for x in fresh['remaining_obligations'] if x!='independent native arithmetic']
        assert row['cell_index']==i and row['analysis']==fresh and not fresh['discovery_claim']
        assert row['native_stdout']=={k:expected_native(fresh[k]).decode('ascii')
                                     for k in ('cleared_integer_terms','primitive_terms')}
    assert receipt['discovery_claim'] is False and receipt['predecessor_ledger_sha256']==PREDECESSOR
    assert receipt['coverage_unit']=='(e,delta,h,b,orientation), all geometrically admissible r'
    # These are immutable experiment evidence, not an append to old ledger:
    # the two parameterizations have different iteration units.
    return total


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);p.add_argument('--replay',type=Path);p.add_argument('--python-only',action='store_true');args=p.parse_args()
    assert sha((ROOT/'data/experiments/index-p19.json').read_bytes())==PREDECESSOR
    if args.replay:
        assert args.output is None and not args.python_only
        print('Fresh complete Python nested-isqrt replay:',replay(args.replay.resolve()));return
    if args.output is None:p.error('--output required')
    folder=args.output.resolve();folder.mkdir(parents=True,exist_ok=False)
    # Native calibration hits Braun, which was excluded by the old ordering;
    # its adjacent b values are independently checked negative controls.
    calibration=[1956878,665,9010,719114,719116]
    cells=plan();results=[];total=[0]*9
    if args.python_only:
        for cell in cells:
            _,counts,hits=oracle(cell);results.append({'cell':cell,'counts':counts,'hits':hits})
            total=[x+y for x,y in zip(total,counts)]
        record={'schema':'E5-TWO-GAP-PYTHON-PILOT-v1','classification':'python_only_provisional','sources':sources(),
                'cells':cells,'results':results,'totals':total,'native_verified':False,'discovery_claim':False}
        (folder/'python-pilot.json').write_bytes(canonical(record));print('Provisional Python only:',total);return
    with tempfile.TemporaryDirectory(prefix='e5-two-gap-') as temp:
        binary=Path(temp)/'search';compile_search(binary)
        cal=run_cell(binary,calibration,folder/'calibration')
        assert len(cal['hits'])==1 and cal['hits'][0][3:7]==[1340632,1331622,1956213,1956878]
        for i,cell in enumerate(cells):
            row=run_cell(binary,cell,folder/f'cell-{i:03d}');results.append(row)
            total=[x+y for x,y in zip(total,row['counts'])]
        candidate_binary=Path(temp)/'candidate';compile_verifier(candidate_binary)
        admissions=[]
        for i,row in enumerate(results):
            for hit in row['hits']:
                proposal=proposal_for(i,row,hit)
                accepted,outputs=verify_native(analyze(proposal),candidate_binary)
                admissions.append({'cell_index':i,'analysis':accepted,'native_stdout':outputs})
        receipt={'schema':'E5-TWO-GAP-BATCH-v1','classification':'bounded_signed_two_gap_search',
          'sources':sources(),'finite_math_kernels_pin':PIN,'source_commit':os.getenv('GITHUB_SHA'),
          'workflow_run_id':os.getenv('GITHUB_RUN_ID'),'predecessor_ledger_sha256':PREDECESSOR,
          'cells':cells,'results':results,'totals':total,'calibration':cal,'candidate_admissions':admissions,
          'discovery_claim':False,'coverage_unit':'(e,delta,h,b,orientation), all geometrically admissible r',
          'limitations':'Only declared cells; one negative summand u>b, all bases <e; not a full height census.'}
        (folder/'receipt.json').write_bytes(canonical(receipt))
    print('Native + independent Python exact two-gap search:',total,'; discovery_claim=false')


if __name__=='__main__':main()
