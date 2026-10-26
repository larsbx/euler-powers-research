"""Gap/overlap, complete-height, malformed record and cumulative accounting tests."""
import copy,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from search_novel_stripes import ROOT, plan, canonical, sha
from coverage_ledger import cells, assert_fresh, missing_gaps, append, summary
from search_discovery_p17 import p17_plan


def refused(f):
    try:f()
    except ValueError:return
    raise AssertionError('unsafe territory accepted')


def main():
    base=json.loads((ROOT/'data/experiments/index-p16.json').read_bytes())
    assert len(cells(base))==30
    assert missing_gaps(base,2760001,'positive',1,1024,1,16)==[5,6,7,9,10,11,12,13,14,15]
    scopes=p17_plan();assert sum(x['pairs_upper_budget'] for x in scopes)==409884672
    refused(lambda:assert_fresh(base,[plan(2760001,4,1024,4096,1,'positive',True)]))
    refused(lambda:assert_fresh(base,[scopes[0],scopes[0]]))
    bad=copy.deepcopy(base);bad['experiments'][1]['cells'][0]['abs_a_min']=False
    refused(lambda:cells(bad))
    repeat=copy.deepcopy(base);repeat['experiments'].append(copy.deepcopy(repeat['experiments'][2]))
    refused(lambda:summary(repeat))
    census=copy.deepcopy(base);census['full_height_censuses']=[{'e_min':2,'e_max':320,'domain':'strictly_positive'}]
    refused(lambda:assert_fresh(census,[plan(144,11,64,4096)]))
    addition={'id':'P17','status':'native_and_independent_full_replay_accepted','prior_coverage_index_sha256':sha(canonical(base)),'trials':409884672,'exact_lookups':0,'primitive_witnesses':0,'witnesses':[],'cells':[{'e':x['e'],'delta':x['delta'],'sign':x['sign'],'abs_a_min':x['a_min'],'abs_a_max':x['a_cap'],'trials':x['pairs_upper_budget'],'exact_lookups':0,'primitive_witnesses':0} for x in scopes]}
    result=append(base,addition)
    assert missing_gaps(result,2760001,'positive',1,1024,1,16)==[]
    r=[x for x in summary(result)['rectangles'] if x['e']==2760001 and x['sign']=='positive']
    assert r[0]['delta_min']==1 and r[0]['delta_max']==16 and r[0]['abs_a_min']==1 and r[0]['abs_a_max']==1024
    assert summary(result)['high_height_exact_trials']==930452224
    bad=copy.deepcopy(addition);bad['trials']+=1;refused(lambda:append(base,bad))
    bad=copy.deepcopy(addition);bad['prior_coverage_index_sha256']='0'*64;refused(lambda:append(base,bad))
    assert len(base['experiments'])==3
    refused(lambda:append(result,addition))
    print('Coverage ledger: exact gap selection, overlap/duplicate/census refusal, malformed-scope refusal and cumulative interval union passed.')

if __name__=='__main__':main()
