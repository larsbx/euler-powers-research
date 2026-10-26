"""Hash-table oracle, exact reconstruction, precompiled Mojo comparison receipts.

Pair boxes are algebra conformance, not E5 discovery coverage. Timings compare
one-query processes, including startup/table initialization, excluding compiler.
"""
import argparse
from hashlib import sha256
from itertools import combinations_with_replacement
import json
from math import isqrt
import os
from pathlib import Path
import subprocess
import tempfile
from time import perf_counter_ns

ROOT=Path(__file__).resolve().parents[1]
PIN='c5b2d3d7879bcf2354d4d9784bd20a6b3dc610fd'
SOURCES=('algebra/pair_sum.mojo','algebra/pair_sum_probe.mojo',
         'tests/test_pair_sum_reconstruction.py','kernel/euler_exact.mojo',
         'kernel/verify_known.mojo','scripts/run_mojo.sh','pixi.toml','pixi.lock')
METHODS=('scan','reconstruct')


def canonical(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def sha(x):return sha256(x).hexdigest()
def target(c):return c['a']**5+c['b']**5+c['offset']


def corpus():
    out=[];seen=set()
    for a,b in combinations_with_replacement(range(-3,4),2):
        R=a**5+b**5
        if R not in seen:
            out.append(dict(bound=8,a=a,b=b,offset=0,repetitions=1));seen.add(R)
    out.extend(dict(bound=8,a=0,b=0,offset=n,repetitions=1) for n in (-3,-2,2,3))
    for B,a,b,n in ((64,-64,3,0),(64,8,63,1),
                     (4096,1025,3183,0),(4096,-4096,2049,0),
                     (8192,4097,8191,0),(8192,-8192,4097,0),
                     (8192,-8192,4097,1),(8192,8191,8192,-1)):
        out.append(dict(bound=B,a=a,b=b,offset=n,repetitions=3))
    return out


def oracle(R,B):
    # No sum/product reconstruction: exact fifth powers and independent dict.
    fifth={x**5:x for x in range(-B,B+1)}
    return [(a,fifth[R-a**5]) for a in range(-B,B+1)
            if R-a**5 in fifth and a<=fifth[R-a**5]]


def reconstruct_python(R,B):
    if R==0:return [(a,-a) for a in range(-B,1)],(0,0,0,B+1)
    out=[];trials=divisors=squares=0
    for s in range(-2*B,2*B+1):
        if not s:continue
        trials+=1
        if R%s:continue
        divisors+=1
        delta=5*s**4+20*(R//s)
        if delta<0:continue
        root=isqrt(delta)
        if root>10*B*B or root*root!=delta:continue
        squares+=1
        num=5*s*s-root
        if num%10:continue
        p=num//10;T=s*s-4*p
        if T<0:continue
        diff=isqrt(T)
        if diff>2*B or diff*diff!=T or (s-diff)%2:continue
        a,b=(s-diff)//2,(s+diff)//2
        if a < -B or b>B:continue
        assert a**5+b**5==R
        out.append((a,b))
    return out,(trials,divisors,squares,len(out))


def expected(c,method):
    R=target(c);B=c['bound'];pairs=oracle(R,B)
    if method=='reconstruct':
        actual,counts=reconstruct_python(R,B)
        assert sorted(actual)==pairs
        pairs=actual
    else:counts=(2*B+1,len(pairs))
    rows=[f'DOMAIN E5-PAIR-SUM-v1 {method} {B} {R}']
    rows+=['PAIR '+str(a)+' '+str(b) for a,b in pairs]
    rows+=['SUMMARY '+' '.join(map(str,counts))]
    return ('\n'.join(rows)+'\n').encode()


def check_python():
    # Every attainable target from this full signed box, plus adjacent controls.
    B=12
    Rs={a**5+b**5 for a in range(-B,B+1) for b in range(a,B+1)}
    for R in Rs|{R+1 for R in Rs}|{R-1 for R in Rs}:
        pairs,_=reconstruct_python(R,B)
        assert sorted(pairs)==oracle(R,B)
    for c in corpus():
        for method in METHODS:expected(c,method)
    # Exact square boundaries mirror native upper sentinels, with no floats.
    for hi in (0,1,4,10):
        for n in range(-1,(hi+1)**2+2):
            root=-1 if n<0 else isqrt(n)
            exact=root if 0<=root<=hi and root*root==n else -1
            assert (exact>=0)==any(x*x==n for x in range(hi+1))
    return len(Rs)


def source_hashes():return {p:sha((ROOT/p).read_bytes()) for p in SOURCES}


def verify(folder):
    r=json.loads((folder/'accepted.json').read_bytes())
    assert r['schema']=='E5-PAIR-SUM-COMPARISON-v1'
    assert r['classification']=='algebra_conformance_only' and r['discovery_trials']==0
    assert r['sources']==source_hashes() and r['finite_math_kernels_sha']==PIN
    assert r['cases']==corpus()
    expected_keys=[(i,m,k) for i,c in enumerate(corpus()) for k in range(c['repetitions']) for m in (METHODS if k%2==0 else METHODS[::-1])]
    assert [(x['case'],x['method'],x['repeat']) for x in r['observations']]==expected_keys
    names={'accepted.json','build-resource.json'}
    assert r['build_resource_sha256']==sha((folder/'build-resource.json').read_bytes())
    sums={m:0 for m in METHODS}
    for x in r['observations']:
        stem=f"case{x['case']:03d}-{x['method']}-{x['repeat']}"
        raw=(folder/(stem+'.txt')).read_bytes();resource=(folder/(stem+'.time')).read_bytes()
        names|={stem+'.txt',stem+'.time'}
        assert raw==expected(corpus()[x['case']],x['method']) and sha(raw)==x['stdout_sha256']
        assert sha(resource)==x['resource_sha256'] and json.loads(resource)==x['resource']
        assert x['wall_ns']>0 and x['resource']['max_rss_kib']>0
        sums[x['method']]+=x['wall_ns']
    assert sums==r['sum_process_wall_ns']
    assert {p.name for p in folder.iterdir()}==names
    return r


def main():
    p=argparse.ArgumentParser();p.add_argument('--python-only',action='store_true')
    p.add_argument('--output',type=Path);p.add_argument('--verify',action='store_true');args=p.parse_args()
    n=check_python()
    if args.python_only:
        assert not args.verify and args.output is None
        print(f'Exact signed reconstruction agrees with hash oracle on {n} attainable small-box targets and adjacent controls; {len(corpus())} native cases planned. No discovery coverage.')
        return
    if args.output is None:p.error('--output required')
    folder=args.output.resolve()
    if args.verify:
        r=verify(folder);print(f"Full independent replay accepted: {len(r['observations'])} precompiled native queries; no discovery credit.");return
    folder.mkdir(parents=True,exist_ok=False)
    observations=[]
    with tempfile.TemporaryDirectory(prefix='e5-pair-binary-') as tmp:
        binary=Path(tmp)/'pair-probe'
        # Caller initializes and verifies the pinned dependency with verify.
        pin=subprocess.check_output(['git','-C',str(ROOT/'.deps/finite-math-kernels'),'rev-parse','HEAD'],text=True).strip()
        assert pin==PIN
        command=['/usr/bin/time','-f','{"wall_seconds":%e,"user_seconds":%U,"system_seconds":%S,"max_rss_kib":%M}',
                 '-o',str(folder/'build-resource.json'),'mojo','build','-I','kernel','-I','algebra',
                 '-I','.deps/finite-math-kernels/kernel','algebra/pair_sum_probe.mojo','-o',str(binary)]
        build=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=300)
        assert build.returncode==0,build.stderr.decode()
        binary_sha=sha(binary.read_bytes())
        for i,c in enumerate(corpus()):
            for k in range(c['repetitions']):
                for method in (METHODS if k%2==0 else METHODS[::-1]):
                    stem=f'case{i:03d}-{method}-{k}';res=folder/(stem+'.time')
                    cmd=['/usr/bin/time','-f','{"wall_seconds":%e,"user_seconds":%U,"system_seconds":%S,"max_rss_kib":%M}',
                         '-o',str(res),str(binary),method,*map(str,(c['bound'],c['a'],c['b'],c['offset']))]
                    started=perf_counter_ns();run=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=60);elapsed=perf_counter_ns()-started
                    assert run.returncode==0,run.stderr.decode()
                    (folder/(stem+'.txt')).write_bytes(run.stdout)
                    assert run.stdout==expected(c,method),f'native mismatch at case {i} {method}'
                    observations.append(dict(case=i,method=method,repeat=k,stdout_sha256=sha(run.stdout),
                                             resource_sha256=sha(res.read_bytes()),resource=json.loads(res.read_bytes()),wall_ns=elapsed))
    receipt=dict(schema='E5-PAIR-SUM-COMPARISON-v1',classification='algebra_conformance_only',discovery_trials=0,
                 sources=source_hashes(),finite_math_kernels_sha=PIN,source_commit=os.getenv('GITHUB_SHA'),github_run_id=os.getenv('GITHUB_RUN_ID'),
                 cases=corpus(),observations=observations,binary_sha256=binary_sha,
                 build_resource_sha256=sha((folder/'build-resource.json').read_bytes()),
                 sum_process_wall_ns={m:sum(x['wall_ns'] for x in observations if x['method']==m) for m in METHODS},
                 measurement='same precompiled binary, interleaved one-query processes including startup and table initialization; compiler measured separately; powers not reused between queries')
    (folder/'accepted.json').write_bytes(canonical(receipt));verify(folder)
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('observations','sources','cases')},sort_keys=True))


if __name__=='__main__':main()
