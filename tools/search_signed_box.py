"""P21: bounded native comparison/search and independent full arithmetic replay.

Receipts credit the declared finite domains only. Missing/mutated files,
source drift, partial completion, broken partitions, or replay disagreement
fail closed. A registry miss is never a novelty certificate.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from itertools import combinations_with_replacement
import json
from math import comb
import os
from pathlib import Path
import resource
import statistics
import subprocess
import tempfile
import time

from primitive_candidates import (analyze, canonical, compile_verifier,
                                 verify_dependency, verify_native)
ROOT=Path(__file__).resolve().parents[1]
PIN='c5b2d3d7879bcf2354d4d9784bd20a6b3dc610fd'
SOURCES=('discovery/signed_box.mojo','algebra/pair_sum.mojo','kernel/bigz_pair_index.mojo',
         'kernel/euler_exact.mojo','kernel/verify_known.mojo','tools/search_signed_box.py',
         'tools/primitive_candidates.py','discovery/verify_candidate.mojo',
         'data/literature/known_primitive_e5_2026-10-26.json','pixi.toml','pixi.lock')
PRODUCTION=[dict(n=1024,small=1024,start=1),dict(n=512,small=256,start=3000001)]
LIMITS=dict(address_mib=32768,ram_mib=768,cpu_seconds=240,wall_seconds=300,max_file_bytes=4194304)


def sha(data):return sha256(data).hexdigest()
def source_hashes():return {p:sha((ROOT/p).read_bytes()) for p in SOURCES}


def magnitudes(n,small,start):
    if not (1<=n<=1024 and 0<=small<=n and 1<=start<=10**9 and (small==n or start>small)):
        raise ValueError('invalid finite magnitude domain')
    return list(range(1,small+1))+list(range(start,start+n-small))


def partition(n,width):
    if not 1<=width<=n:raise ValueError('invalid shard width')
    return [(a,min(a+width-1,n)) for a in range(1,n+1,width)]


def check_partition(n,parts):
    if not parts or parts[0][0]!=1 or parts[-1][1]!=n:raise ValueError('incomplete partition')
    previous=0
    for a,b in parts:
        if a!=previous+1 or b<a or b>n:raise ValueError('gap/overlap/reversal in partition')
        previous=b


def oracle(case,method,low=1,high=None):
    """Independent Python integer hash index: full signed Cartesian pairs.

    All powers/targets are recomputed in Python. No reconstruction, native
    checksums, sorted BigZ search or native hits feed this enumeration.
    """
    n=case['n'];high=n if high is None else high
    S=magnitudes(n,case['small'],case['start']);xs=[-x for x in reversed(S)]+S
    powers={x:x**5 for x in xs};index={}
    for a,b in combinations_with_replacement(xs,2):
        value=powers[a]+powers[b]
        if value<0:index.setdefault(value,[]).append((a,b))
    lines=[f"DOMAIN E5-SIGNED-BOX-v1 {method} {n} {low} {high} {case['small']} {case['start']} {n*n if method=='index' else 0}"]
    total=hits=0;all_hits=[]
    for ci in range(low-1,high):
        c=S[ci];count=row_hits=checksum=0
        for di in range(ci,n):
            d=S[di];cd=powers[c]+powers[d]
            for ei in range(di,n):
                e=S[ei];target=-cd-powers[e];count+=1;checksum+=target
                for a,b in index.get(target,()):
                    if b>c:continue
                    terms=(a,b,c,d,e)
                    if any(-x in terms for x in terms):continue
                    if sum(x**5 for x in terms)!=0:raise ValueError('oracle arithmetic bug')
                    lines.append('HIT '+' '.join(map(str,terms)));all_hits.append(terms);row_hits+=1
        if count!=comb(n-ci+1,2):raise ValueError('oracle row count')
        lines.append(f'ROW {ci+1} {count} {row_hits} {checksum}')
        total+=count;hits+=row_hits
    lines.append(f'COMPLETE {total} {hits}')
    return ('\n'.join(lines)+'\n').encode('ascii'),all_hits


def limits_setup(limits):
    resource.setrlimit(resource.RLIMIT_AS,(limits['address_mib']*1024**2,)*2)
    resource.setrlimit(resource.RLIMIT_CPU,(limits['cpu_seconds'],)*2)
    resource.setrlimit(resource.RLIMIT_FSIZE,(limits['max_file_bytes'],)*2)


def measured(command,folder,stem,limits=LIMITS):
    """wait4 reports per-child rusage; no cumulative RSS or compiler mixing."""
    started=time.perf_counter_ns()
    with (folder/(stem+'.txt')).open('wb') as out,(folder/(stem+'.err')).open('wb') as err:
        child=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=err,preexec_fn=lambda:limits_setup(limits))
        while True:
            pid,status,usage=os.wait4(child.pid,os.WNOHANG)
            if pid:break
            if (time.perf_counter_ns()-started)/1e9>limits['wall_seconds']:
                child.kill();pid,status,usage=os.wait4(child.pid,0)
                child.returncode=os.waitstatus_to_exitcode(status)
                raise ValueError('wall limit exceeded: '+stem)
            time.sleep(.01)
        child.returncode=os.waitstatus_to_exitcode(status)
    result=dict(exit_code=child.returncode,wall_ns=time.perf_counter_ns()-started,
                user_seconds=usage.ru_utime,system_seconds=usage.ru_stime,max_rss_kib=usage.ru_maxrss,limits=limits)
    (folder/(stem+'.resource.json')).write_bytes(canonical(result))
    if usage.ru_maxrss>limits['ram_mib']*1024:raise ValueError('observed physical memory limit exceeded: '+stem)
    if child.returncode:raise ValueError('failed native process '+stem+': '+(folder/(stem+'.err')).read_text())
    return result


def output_hits(raw):
    return [tuple(map(int,l.split()[1:])) for l in raw.decode('ascii').splitlines() if l.startswith('HIT ')]


def classify(hits,binary=None):
    classes={};imprimitive=0
    for terms in hits:
        proposal=dict(schema='E5-CANDIDATE-PROPOSAL-v1',method='P21 complete signed pair/triple enumeration',
                      provenance='Native transcript independently replayed over the declared finite magnitude set',terms=list(map(str,terms)))
        a=analyze(proposal)
        if a['cleared_integer_gcd']!='1':imprimitive+=1
        key=tuple(a['canonical_class'])
        if key not in classes:
            if binary is None:classes[key]=a
            else:classes[key]=verify_native(a,binary)[0]
    return dict(raw_hits=len(hits),imprimitive_hits=imprimitive,classes=list(classes.values()),
                genuinely_new_primitive_classes=0,discovery_claim=False)


def safe_stem(stem):
    return type(stem) is str and __import__('re').fullmatch(r'[a-z0-9_-]+',stem) is not None


def verify(folder,receipt_name='accepted.json'):
    r=json.loads((folder/receipt_name).read_bytes())
    if r['schema']!='E5-P21-SIGNED-BOX-v1' or r['sources']!=source_hashes() or r['finite_math_kernels_pin']!=PIN:
        raise ValueError('foreign or modified source/receipt')
    if r['production_domains']!=PRODUCTION or r['limits']!=LIMITS:raise ValueError('domain/limits drift')
    names={receipt_name}
    if len({x['stem'] for x in r['observations']})!=len(r['observations']):raise ValueError('duplicate process stem')
    for x in r['observations']:
        stem=x['stem']
        if not safe_stem(stem):raise ValueError('unsafe process stem')
        expected_limits=dict(LIMITS,ram_mib=2048) if x['kind']=='build' else LIMITS
        usage=x['resource']
        if usage['limits']!=expected_limits or usage['max_rss_kib']>expected_limits['ram_mib']*1024:
            raise ValueError('resource limit drift')
        if usage['wall_ns']>expected_limits['wall_seconds']*10**9 or usage['user_seconds']+usage['system_seconds']>expected_limits['cpu_seconds']+1:
            raise ValueError('resource budget exceeded')
        for suffix in ('.txt','.err','.resource.json'):
            name=stem+suffix;names.add(name)
            if sha((folder/name).read_bytes())!=x['files'][suffix]:raise ValueError('mutated process evidence')
        if json.loads((folder/(stem+'.resource.json')).read_bytes())!=x['resource']:raise ValueError('resource drift')
        if x['resource']['exit_code']!=0 or x['resource']['wall_ns']<=0 or x['resource']['max_rss_kib']<=0:
            raise ValueError('incomplete native observation')
    if [x['kind'] for x in r['observations']].count('build')!=2 or [x['stem'] for x in r['observations'][:2]]!=['build','build-verifier']:
        raise ValueError('missing compiler evidence')
    if any(x['kind'] not in ('build','comparison','production','candidate') for x in r['observations']):raise ValueError('foreign observation')
    comparisons=[x for x in r['observations'] if x['kind']=='comparison']
    expected=[(n,k,m) for n in (16,24,32) for k in range(3) for m in (('index','reconstruct') if k%2==0 else ('reconstruct','index'))]
    if [(x['case']['n'],x['repeat'],x['method']) for x in comparisons]!=expected:raise ValueError('comparison corpus drift')
    medians={m:statistics.median(x['resource']['wall_ns'] for x in comparisons if x['method']==m) for m in ('index','reconstruct')}
    if r['strategy_median_wall_ns']!=medians or medians['index']>=medians['reconstruct'] or r['selected_method']!='index':
        raise ValueError('unsupported strategy choice')
    for x in comparisons:
        expected_bytes,_=oracle(x['case'],x['method'])
        if (folder/(x['stem']+'.txt')).read_bytes()!=expected_bytes:raise ValueError('comparison replay mismatch')
    observations=[x for x in r['observations'] if x['kind']=='production'];all_hits=[];trials=0
    if len(observations)!=sum(len(partition(c['n'],128)) for c in PRODUCTION) or any(x['method']!='index' or x['case'] not in PRODUCTION for x in observations):
        raise ValueError('foreign production observations')
    for case in PRODUCTION:
        shards=[x for x in observations if x['case']==case]
        parts=[tuple(x['part']) for x in shards];check_partition(case['n'],parts)
        if parts!=partition(case['n'],128):raise ValueError('foreign production partition')
        # One independent whole-domain traversal, then split the expected rows.
        expected_bytes,hits=oracle(case,'index');all_hits+=hits;trials+=comb(case['n']+2,3)
        lines=expected_bytes.decode('ascii').splitlines();rows={};pending=[]
        for l in lines[1:-1]:
            pending.append(l)
            if l.startswith('ROW '):rows[int(l.split()[1])]=pending;pending=[]
        for x in shards:
            lo,hi=x['part'];body=[l for c in range(lo,hi+1) for l in rows[c]]
            count=sum(comb(case['n']-c+2,2) for c in range(lo,hi+1));nhits=sum(l.startswith('HIT ') for l in body)
            header=f"DOMAIN E5-SIGNED-BOX-v1 index {case['n']} {lo} {hi} {case['small']} {case['start']} {case['n']**2}"
            raw=('\n'.join([header,*body,f'COMPLETE {count} {nhits}'])+'\n').encode('ascii')
            if raw!=(folder/(x['stem']+'.txt')).read_bytes():raise ValueError('production replay mismatch')
    classified=classify(all_hits)
    # Native-verified status is backed by separate arithmetic subprocess evidence.
    for row in classified['classes']:
        row['native_verified']=True
        row['remaining_obligations']=[x for x in row['remaining_obligations'] if x!='independent native arithmetic']
    if classified!=r['candidate_classification'] or r['triple_targets']!=trials:raise ValueError('classification/count drift')
    for x in r['observations']:
        if x['kind']=='candidate':
            terms=x['terms'];expected=f"RESULT E5-CANDIDATE-v1 0 {__import__('math').gcd(*map(int,terms))} 1\n".encode()
            if (folder/(x['stem']+'.txt')).read_bytes()!=expected:raise ValueError('candidate arithmetic mismatch')
    required=[(i,label) for i,a in enumerate(classified['classes']) for label in ('cleared_integer_terms','primitive_terms')]
    candidates=[x for x in r['observations'] if x['kind']=='candidate']
    if [(x['class_index'],x['label']) for x in candidates]!=required:raise ValueError('missing native candidate evidence')
    for x in candidates:
        if x['terms']!=classified['classes'][x['class_index']][x['label']]:raise ValueError('foreign native candidate')
    if {p.name for p in folder.iterdir()}!=names:raise ValueError('foreign/missing output file')
    return r


def publish(folder,receipt):
    # Provisional evidence stays provisional after mismatch, interruption or crash.
    with (folder/'pending.json').open('xb') as f:f.write(canonical(receipt))
    verify(folder,'pending.json')
    os.replace(folder/'pending.json',folder/'accepted.json')


def execute(folder):
    verify_dependency();initial_sources=source_hashes();folder.mkdir(parents=True,exist_ok=False);obs=[]
    def observe(stem,command,**fields):
        limits=dict(LIMITS,ram_mib=2048) if fields.get('kind')=='build' else LIMITS
        usage=measured(command,folder,stem,limits)
        files={s:sha((folder/(stem+s)).read_bytes()) for s in ('.txt','.err','.resource.json')}
        obs.append(dict(stem=stem,resource=usage,files=files,**fields))
        return (folder/(stem+'.txt')).read_bytes()
    with tempfile.TemporaryDirectory(prefix='e5-p21-') as tmp:
        binary=Path(tmp)/'search';verifier=Path(tmp)/'verify'
        build=['mojo','build','-I','kernel','-I','algebra','-I','.deps/finite-math-kernels/kernel','discovery/signed_box.mojo','-o',str(binary)]
        observe('build',build,kind='build')
        observe('build-verifier',['mojo','build','-I','.deps/finite-math-kernels/kernel','discovery/verify_candidate.mojo','-o',str(verifier)],kind='build')
        for n in (16,24,32):
            case=dict(n=n,small=n,start=1)
            for k in range(3):
                for method in (('index','reconstruct') if k%2==0 else ('reconstruct','index')):
                    raw=observe(f'compare-{n}-{k}-{method}',[str(binary),method,str(n),'1',str(n),str(n),'1'],
                                kind='comparison',case=case,repeat=k,method=method)
                    if raw!=oracle(case,method)[0]:raise ValueError('native comparison disagreement')
        medians={m:statistics.median(x['resource']['wall_ns'] for x in obs if x['kind']=='comparison' and x['method']==m) for m in ('index','reconstruct')}
        if medians['index']>=medians['reconstruct']:raise ValueError('indexed strategy not supported by measurements')
        hits=[]
        for i,case in enumerate(PRODUCTION):
            for lo,hi in partition(case['n'],128):
                print(f"native domain {i} c={lo}..{hi}",flush=True)
                raw=observe(f'production-{i}-{lo:04d}-{hi:04d}',[str(binary),'index',str(case['n']),str(lo),str(hi),str(case['small']),str(case['start'])],
                            kind='production',case=case,part=[lo,hi],method='index')
                hits+=output_hits(raw)
        result=classify(hits,verifier)
        for i,a in enumerate(result['classes']):
            for label in ('cleared_integer_terms','primitive_terms'):
                observe(f'candidate-{i}-{label}',[str(verifier),*a[label]],kind='candidate',class_index=i,label=label,terms=a[label])
        r=dict(schema='E5-P21-SIGNED-BOX-v1',sources=initial_sources,finite_math_kernels_pin=PIN,
               production_domains=PRODUCTION,limits=LIMITS,observations=obs,selected_method='index',strategy_median_wall_ns=medians,
               candidate_classification=result,triple_targets=sum(comb(c['n']+2,3) for c in PRODUCTION),
               source_commit=os.getenv('GITHUB_SHA'),workflow_run_id=os.getenv('GITHUB_RUN_ID'),
               global_nonexistence_claim=False,binary_sha256=sha(binary.read_bytes()))
        publish(folder,r)
    return r


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--verify',action='store_true');args=p.parse_args()
    r=(verify if args.verify else execute)(args.output.resolve())
    print(json.dumps(dict(triple_targets=r['triple_targets'],classification=r['candidate_classification'],
                          selected_method=r['selected_method'],strategy_median_wall_ns=r['strategy_median_wall_ns']),sort_keys=True))
if __name__=='__main__':main()
