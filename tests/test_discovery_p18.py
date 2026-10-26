"""Reviewed new P18 scopes, exact work and disjoint cumulative accounting."""
import copy
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from search_novel_stripes import ROOT, canonical, sha, plan
from search_discovery_p18 import p18_plan, INDEX
from coverage_ledger import assert_fresh, append, cells, missing_gaps, summary, certified_addition


def refused(f):
    try:f()
    except ValueError:return
    raise AssertionError('invalid/overlapping plan accepted')


def main():
    baseline=json.loads(INDEX.read_bytes())
    scopes=p18_plan()
    assert len(cells(baseline))==40 and len(scopes)==16
    assert [c['delta'] for c in scopes]==list(range(17,33))
    assert sum(c['pairs_upper_budget'] for c in scopes)==786334720
    assert all(c['e']==2760001 and c['a_min']==1 and c['a_cap']==1024
               and c['sign']=='positive' and c['bound_mode']=='two_term' for c in scopes)
    for c in scopes:
        D=c['e']**5-(c['e']-c['delta'])**5
        assert 1024**5+2*(c['c_min']-1)**5<D<=1024**5+2*c['c_min']**5
        assert c['c_max']**5<=D<(c['c_max']+1)**5
    refused(lambda:assert_fresh(baseline,[plan(2760001,16,1024,4096,1,'positive',True)]))
    refused(lambda:assert_fresh(baseline,[scopes[0],scopes[0]]))
    refused(lambda:certified_addition({}, {}, ROOT, [], Path(__file__),experiment_id='unreviewed'))
    # Synthetic zero-lookup receipt ONLY exercises ledger union; it is not
    # written, admitted by the native controller, or presented as evidence.
    addition={'id':'P18','status':'native_and_independent_full_replay_accepted',
              'prior_coverage_index_sha256':sha(canonical(baseline)),
              'trials':786334720,'exact_lookups':0,'primitive_witnesses':0,'witnesses':[],
              'cells':[{'e':c['e'],'delta':c['delta'],'sign':c['sign'],
                        'abs_a_min':c['a_min'],'abs_a_max':c['a_cap'],
                        'trials':c['pairs_upper_budget'],'exact_lookups':0,'primitive_witnesses':0} for c in scopes]}
    result=append(baseline,addition)
    assert missing_gaps(result,2760001,'positive',1,1024,1,32)==[]
    assert summary(result)['high_height_exact_trials']==1716786944
    assert len(cells(result))==56
    assert len(cells(baseline))==40
    bad=copy.deepcopy(addition);bad['trials']+=1
    refused(lambda:append(baseline,bad))
    refused(lambda:append(result,addition))
    print('P18 exact bounds, 786334720 finite work, predecessor, overlap and cumulative-union checks passed (synthetic accounting tests only).')


if __name__=='__main__':main()
