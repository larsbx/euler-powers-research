"""P17 fills untouched positive gaps through delta=16 and certifies coverage logs."""
import argparse
import json
from pathlib import Path
from search_novel_stripes import ROOT, canonical, plan, sha
from search_discovery_frontier import main as run_frontier
from coverage_ledger import assert_fresh, missing_gaps, certified_addition

INDEX=ROOT/'data/experiments/index-p16.json'
DELTAS=(5,6,7,9,10,11,12,13,14,15)


def p17_plan():
    baseline=json.loads(INDEX.read_bytes())
    if missing_gaps(baseline,2760001,'positive',1,1024,1,16)!=list(DELTAS):
        raise ValueError('P17 prior coverage differs from reviewed untouched frontier')
    cells=[plan(2760001,d,1024,4096,1,'positive',True) for d in DELTAS]
    assert_fresh(baseline,cells)
    if len(cells)!=10 or sum(c['pairs_upper_budget'] for c in cells)>420_000_000:
        raise ValueError('P17 finite resource budget exceeded')
    return cells


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--verify',action='store_true')
    args=ap.parse_args();baseline=json.loads(INDEX.read_bytes());expected=p17_plan()
    run_frontier(cells=expected,receipt_name='accepted-p17.json',controller_path=Path(__file__),schema='E5-DISCOVERY-P17-v1',
                 extra={'prior_coverage_index_sha256':sha(canonical(baseline)),
                        'prior_coverage_file_sha256':sha(INDEX.read_bytes()),
                        'coverage_ledger_sha256':sha((ROOT/'tools/coverage_ledger.py').read_bytes())})
    folder=args.output.resolve();record=json.loads((folder/'accepted-p17.json').read_bytes())
    addition=certified_addition(baseline,record,folder,expected,Path(__file__))
    target=folder/'coverage-addition.json'
    if args.verify:
        if target.read_bytes()!=canonical(addition):raise ValueError('changed/missing cumulative territory receipt')
    else:
        with target.open('xb') as f:f.write(canonical(addition))
    print('COVERAGE LOG ACCEPTED: ten disjoint complete positive cells; no historical trial double counting.',flush=True)

if __name__=='__main__':main()
