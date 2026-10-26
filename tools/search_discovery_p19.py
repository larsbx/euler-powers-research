"""P19 searches new minimum summands 1025..4096 with exact coverage receipts."""
import argparse
import json
from pathlib import Path
from search_novel_stripes import ROOT, canonical, plan, sha
from search_discovery_frontier import main as run_frontier
from coverage_ledger import assert_fresh, missing_gaps, certified_addition

INDEX=ROOT/'data/experiments/index-p18.json'
PARAMETERS=((1,'positive'),(2,'positive'),(3,'positive'),(4,'positive'),(8,'positive'),(16,'positive'),(4,'negative'))


def p19_plan():
    baseline=json.loads(INDEX.read_bytes())
    cells=[plan(2760001,d,4096,4096,1025,sign,True) for d,sign in PARAMETERS]
    assert_fresh(baseline,cells)
    if len(cells)!=7 or sum(c['pairs_upper_budget'] for c in cells)>800_000_000:
        raise ValueError('P19 finite resource budget exceeded')
    return cells


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--verify',action='store_true')
    args=ap.parse_args();baseline=json.loads(INDEX.read_bytes());expected=p19_plan()
    run_frontier(cells=expected,receipt_name='accepted-p19.json',controller_path=Path(__file__),schema='E5-DISCOVERY-P19-v1',
                 extra={'prior_coverage_index_sha256':sha(canonical(baseline)),
                        'prior_coverage_file_sha256':sha(INDEX.read_bytes()),
                        'coverage_ledger_sha256':sha((ROOT/'tools/coverage_ledger.py').read_bytes())})
    folder=args.output.resolve();record=json.loads((folder/'accepted-p19.json').read_bytes())
    addition=certified_addition(baseline,record,folder,expected,Path(__file__),experiment_id='P19')
    target=folder/'coverage-addition.json'
    if args.verify:
        if target.read_bytes()!=canonical(addition):raise ValueError('changed/missing cumulative territory receipt')
    else:
        with target.open('xb') as f:f.write(canonical(addition))
    print('COVERAGE LOG ACCEPTED: seven disjoint complete larger-minimum-summand cells; no historical trial double counting.',flush=True)

if __name__=='__main__':main()
