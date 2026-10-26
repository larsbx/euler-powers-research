"""Same production stripes, precompiled before/after, exact independent replay.

Before is the accepted pre-P19 source with ONLY its A intake guard relaxed.
No benchmark query receives Euler discovery credit; full cells run separately.
"""
import argparse,json,os,subprocess,sys,tempfile
from pathlib import Path
from time import perf_counter_ns
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from search_novel_stripes import ROOT,plan,canonical,sha,independent_oracle

BEFORE='benchmarks/native/stripe_before_p19.mojo'
AFTER='kernel/near_cancellation_stripe.mojo'
OLD_SHA='365a415ea60b9270b0c5845663e42dc6f55b9dd67680f66e001b47fbc9c1227d'
PIN='c5b2d3d7879bcf2354d4d9784bd20a6b3dc610fd'
SOURCES=(BEFORE,AFTER,'kernel/near_cancellation.mojo','kernel/euler_exact.mojo',
         'tests/benchmark_residue_first.py','tools/search_novel_stripes.py','scripts/run_mojo.sh','pixi.toml','pixi.lock')


def cases():
    out=[]
    for e,d,A,amin,sign,lo,hi in ((144,11,4096,1,'positive',93,115),
                                  (85359,77,4096,1,'positive',28965,28969),
                                  (14132,64,4096,1,'negative',6237,6237)):
        c=plan(e,d,A,4096,amin,sign,True);out.append({'scope':c,'lo':lo,'hi':hi,'repetitions':1,'classification':'calibration'})
    for d,sign in ((1,'positive'),(4,'negative'),(16,'positive')):
        c=plan(2760001,d,4096,4096,1025,sign,True)
        lo=c['c_min'] if d!=16 else (c['c_min']+c['c_max'])//2
        out.append({'scope':c,'lo':lo,'hi':lo+4095,'repetitions':3,'classification':'production_stripe_comparison_only'})
    return out


def sources():return {p:sha((ROOT/p).read_bytes()) for p in SOURCES}


def expected(c):
    s=c['scope']
    return independent_oracle(s['e'],s['delta'],s['a_cap'],c['lo'],c['hi'],s).encode('ascii')


def baseline_guard_check():
    text=(ROOT/BEFORE).read_text()
    assert text.count('max_a > 4096')==1
    assert sha(text.replace('max_a > 4096','max_a > 1024').encode())==OLD_SHA


def verify(folder,reference):
    r=json.loads((folder/'accepted.json').read_bytes())
    assert r['schema']=='E5-RESIDUE-FIRST-COMPARISON-v1' and r['discovery_trials']==0
    assert r['sources']==sources() and r['cases']==cases() and r['finite_math_kernels_pin']==PIN
    keys=[(i,m,k) for i,c in enumerate(cases()) for k in range(c['repetitions']) for m in (('before','after') if k%2==0 else ('after','before'))]
    assert [(x['case'],x['method'],x['repeat']) for x in r['observations']]==keys
    names={'accepted.json'};sums={m:0 for m in ('before','after')}
    for m in sums:
        name=m+'-build.time';names.add(name)
        assert sha((folder/name).read_bytes())==r['build_resources'][m]['sha256']
        assert json.loads((folder/name).read_bytes())==r['build_resources'][m]['resource']
    for x in r['observations']:
        stem=f"case{x['case']}-{x['method']}-{x['repeat']}"
        raw=(folder/(stem+'.txt')).read_bytes();resource=(folder/(stem+'.time')).read_bytes();names|={stem+'.txt',stem+'.time'}
        assert raw==reference[x['case']] and sha(raw)==x['stdout_sha256']
        assert sha(resource)==x['resource_sha256'] and json.loads(resource)==x['resource']
        assert x['process_wall_ns']>0 and x['resource']['max_rss_kib']>0
        sums[x['method']]+=x['process_wall_ns']
    assert r['sum_process_wall_ns']==sums
    assert {p.name for p in folder.iterdir()}==names
    return r


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--verify',action='store_true');args=p.parse_args()
    baseline_guard_check();reference=[expected(c) for c in cases()];folder=args.output.resolve()
    if args.verify:
        r=verify(folder,reference);print(f"Production stripe before/after full Python replay accepted: {len(r['observations'])} queries, zero discovery credit.");return
    folder.mkdir(parents=True,exist_ok=False)
    assert subprocess.check_output(['git','-C',str(ROOT/'.deps/finite-math-kernels'),'rev-parse','HEAD'],text=True).strip()==PIN
    obs=[];builds={};binary_hashes={}
    fmt='{"wall_seconds":%e,"user_seconds":%U,"system_seconds":%S,"max_rss_kib":%M}'
    with tempfile.TemporaryDirectory(prefix='e5-residue-first-') as tmp:
        bins={}
        for m,source in (('before',BEFORE),('after',AFTER)):
            binary=Path(tmp)/m;res=folder/(m+'-build.time')
            cmd=['/usr/bin/time','-f',fmt,'-o',str(res),'mojo','build','-I','kernel','-I','.deps/finite-math-kernels/kernel',source,'-o',str(binary)]
            run=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=300)
            assert run.returncode==0,run.stderr.decode()
            bins[m]=binary;binary_hashes[m]=sha(binary.read_bytes());builds[m]={'sha256':sha(res.read_bytes()),'resource':json.loads(res.read_bytes())}
        for i,c in enumerate(cases()):
            s=c['scope'];fields=[s['e'],s['delta'],s['a_cap'],c['lo'],c['hi'],s['a_min'],int(s['sign']=='negative'),1]
            for k in range(c['repetitions']):
                for m in (('before','after') if k%2==0 else ('after','before')):
                    stem=f'case{i}-{m}-{k}';res=folder/(stem+'.time')
                    cmd=['/usr/bin/time','-f',fmt,'-o',str(res),str(bins[m]),*map(str,fields)]
                    started=perf_counter_ns();run=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=120);elapsed=perf_counter_ns()-started
                    (folder/(stem+'.txt')).write_bytes(run.stdout)
                    assert run.returncode==0,run.stderr.decode()
                    assert run.stdout==reference[i],(i,m,'production transcript mismatch')
                    obs.append({'case':i,'method':m,'repeat':k,'process_wall_ns':elapsed,'resource':json.loads(res.read_bytes()),'resource_sha256':sha(res.read_bytes()),'stdout_sha256':sha(run.stdout)})
    r={'schema':'E5-RESIDUE-FIRST-COMPARISON-v1','classification':'production_stripe_conformance_and_timing','discovery_trials':0,
       'source_commit':os.getenv('GITHUB_SHA'),'workflow_run_id':os.getenv('GITHUB_RUN_ID'),'finite_math_kernels_pin':PIN,
       'sources':sources(),'before_original_sha256':OLD_SHA,'cases':cases(),'observations':obs,'build_resources':builds,
       'binary_sha256':binary_hashes,'sum_process_wall_ns':{m:sum(x['process_wall_ns'] for x in obs if x['method']==m) for m in bins},
       'measurement':'Precompiled original production stripe before/after. Includes process startup, exact power-cache and residue-prefix construction. Compilation measured separately. Three repetitions per large stripe.'}
    (folder/'accepted.json').write_bytes(canonical(r));verify(folder,reference)
    print(json.dumps({k:v for k,v in r.items() if k not in ('sources','cases','observations')},sort_keys=True))


if __name__=='__main__':main()
