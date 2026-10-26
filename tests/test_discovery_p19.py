"""New larger-a scopes, exact bounds, cap edges and disjoint accounting."""
import copy,json,sys,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from search_novel_stripes import ROOT,plan,canonical,sha,independent_oracle
from search_discovery_p19 import p19_plan,INDEX
from coverage_ledger import append,assert_fresh,cells,summary


def refused(f):
    try:f()
    except ValueError:return
    raise AssertionError('invalid or repeated scope accepted')


def main():
    base=json.loads(INDEX.read_bytes());scopes=p19_plan()
    assert len(cells(base))==56 and len(scopes)==7
    assert sum(c['pairs_upper_budget'] for c in scopes)==724549632
    assert all(c['a_min']==1025 and c['a_cap']==4096 and c['e']==2760001 for c in scopes)
    assert [(c['delta'],c['sign']) for c in scopes]==[(d,'positive') for d in (1,2,3,4,8,16)]+[(4,'negative')]
    for c in scopes:
        D=c['e']**5-c['d']**5;threshold=D-(4096**5 if c['sign']=='positive' else 0)
        assert 2*(c['c_min']-1)**5<threshold<=2*c['c_min']**5
        upper=D+(4096**5 if c['sign']=='negative' else 0)
        assert c['c_max']**5<=upper<(c['c_max']+1)**5
    refused(lambda:plan(2760001,1,4097,4096,1025,'positive',True))
    refused(lambda:assert_fresh(base,[plan(2760001,1,4096,4096,1024,'positive',True)]))
    refused(lambda:assert_fresh(base,[scopes[0],scopes[0]]))
    addition={'id':'P19','status':'native_and_independent_full_replay_accepted','prior_coverage_index_sha256':sha(canonical(base)),
              'trials':724549632,'exact_lookups':0,'primitive_witnesses':0,'witnesses':[],
              'cells':[{'e':c['e'],'delta':c['delta'],'sign':c['sign'],'abs_a_min':c['a_min'],'abs_a_max':c['a_cap'],
                        'trials':c['pairs_upper_budget'],'exact_lookups':0,'primitive_witnesses':0} for c in scopes]}
    # Pure synthetic accounting fixture, never published as native evidence.
    result=append(base,addition)
    assert len(cells(result))==63 and summary(result)['high_height_exact_trials']==2441336576
    assert len(cells(base))==56
    if '--python-only' not in sys.argv:
        for c in scopes:
            lo=c['c_min'];hi=lo+7
            args=[c['e'],c['delta'],4096,lo,hi,1025,int(c['sign']=='negative'),1]
            r=subprocess.run(['bash','scripts/run_mojo.sh','kernel/near_cancellation_stripe.mojo',*map(str,args)],cwd=ROOT,capture_output=True,text=True,timeout=120)
            assert r.returncode==0,r.stderr
            assert r.stdout==independent_oracle(c['e'],c['delta'],4096,lo,hi,c)
        # Valid c bounds make this specifically an out-of-policy A refusal.
        c=scopes[0]
        r=subprocess.run(['bash','scripts/run_mojo.sh','kernel/near_cancellation_stripe.mojo',*map(str,(2760001,1,4097,c['c_min'],c['c_min']+1,1025,0,1))],cwd=ROOT,capture_output=True,text=True,timeout=120)
        assert r.returncode!=0
    print('P19 exact bounds, 724549632 budget, fresh a=1025..4096, cap guard and cumulative accounting passed; '+('native controls skipped by --python-only.' if '--python-only' in sys.argv else 'native controls passed.'))


if __name__=='__main__':main()
