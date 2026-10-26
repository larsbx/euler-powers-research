"""P16: new |a|=257..1024 cells with proven two-term enclosing bounds."""
from pathlib import Path
import json
from search_novel_stripes import ROOT, plan, sha
from search_discovery_frontier import main as run_frontier

INDEX = ROOT/'data/experiments/index.json'
PARAMETERS = [(d,'positive') for d in (1,2,3,4,8,16,64,256)] + [(d,'negative') for d in (4,16)]


def p16_plan():
    cells = [plan(2760001,d,1024,4096,257,sign,True) for d,sign in PARAMETERS]
    if len(cells)>10 or sum(c['pairs_upper_budget'] for c in cells)>320_000_000:
        raise ValueError('P16 finite work budget exceeded')
    prior=json.loads(INDEX.read_text())
    old_cells=[]
    for experiment in prior['experiments']:
        if experiment['id']=='P14':
            p=experiment['parameters']
            old_cells.extend({'e':e,'delta':d,'sign':'positive','abs_a_min':p['positive_a_interval'][0],'abs_a_max':p['positive_a_interval'][1]} for e in p['e'] for d in p['delta'])
        elif experiment['id']=='P15':
            old_cells.extend(experiment['cells'])
    if not old_cells:
        raise ValueError('missing accepted prior coverage')
    seen=set()
    for c in cells:
        key=(c['e'],c['delta'],c['sign'],c['a_min'],c['a_cap'])
        if key in seen:raise ValueError('duplicate P16 cell')
        seen.add(key)
        for old in old_cells:
            if (c['e'],c['delta'],c['sign'])==(old['e'],old['delta'],old['sign']):
                if max(c['a_min'],old['abs_a_min'])<=min(c['a_cap'],old['abs_a_max']):
                    raise ValueError('P16 overlaps prior accepted coverage')
    return cells


if __name__=='__main__':
    run_frontier(cells=p16_plan(),receipt_name='accepted-p16.json',controller_path=Path(__file__),
                 schema='E5-DISCOVERY-P16-v1',extra={'prior_coverage_index_sha256':sha(INDEX.read_bytes()),
                 'bound_meaning':'positive: D<=A^5+2c^5; negative: D<=2c^5; no valid witness occurs below the certified c_min'})
