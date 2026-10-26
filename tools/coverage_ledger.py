"""Finite E5 territory: disjoint admission, source receipts, explicit coverage unions.

Coverage admission follows full independent replay. It does not authenticate a
remote worker or turn declared plans/calibration-only tests into accepted cells.
"""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
from collections import defaultdict
from search_novel_stripes import ROOT, canonical, plan, sha, source_identity
from search_discovery_frontier import cell_id, verify_cell


def integer(x):
    if type(x) is not int or x<0:raise ValueError('noncanonical ledger integer')
    return x


def cells(ledger):
    rows=[]
    for exp in ledger['experiments']:
        if exp['id']=='P14':
            p=exp['parameters']
            for e in p['e']:
                for d in p['delta']:
                    rows.append({'experiment':exp['id'],'e':e,'delta':d,'sign':'positive',
                                 'abs_a_min':p['positive_a_interval'][0],'abs_a_max':p['positive_a_interval'][1]})
        else:
            for row in exp['cells']:
                rows.append({**row,'experiment':exp['id']})
    for r in rows:
        for k in ('e','delta','abs_a_min','abs_a_max'):integer(r[k])
        if not 1<=r['delta']<r['e'] or not 1<=r['abs_a_min']<=r['abs_a_max'] or r['sign'] not in ('positive','negative'):
            raise ValueError('invalid accepted cell scope')
    for i,r in enumerate(rows):
        for other in rows[:i]:
            if key(r)==key(other) and intersects(r['abs_a_min'],r['abs_a_max'],other['abs_a_min'],other['abs_a_max']):
                raise ValueError('accepted ledger double-counts territory')
    return rows


def key(r):return r['e'],r['delta'],r['sign']
def intersects(a,b,c,d):return max(a,c)<=min(b,d)


def assert_fresh(ledger, scopes):
    old=cells(ledger)
    seen=[]
    for scope in scopes:
        r={'e':scope['e'],'delta':scope['delta'],'sign':scope['sign'],
           'abs_a_min':scope['a_min'],'abs_a_max':scope['a_cap']}
        for other in old+seen:
            if key(r)==key(other) and intersects(r['abs_a_min'],r['abs_a_max'],other['abs_a_min'],other['abs_a_max']):
                raise ValueError('new plan overlaps already covered or repeated territory')
        for census in ledger.get('full_height_censuses',[]):
            if r['sign']=='positive' and census['e_min']<=r['e']<=census['e_max']:
                raise ValueError('new plan repeats a full-height census')
        seen.append(r)


def intervals(ledger,e,delta,sign):
    values=sorted((r['abs_a_min'],r['abs_a_max']) for r in cells(ledger) if key(r)==(e,delta,sign))
    merged=[]
    for lo,hi in values:
        if merged and lo<=merged[-1][1]+1:merged[-1][1]=max(hi,merged[-1][1])
        else:merged.append([lo,hi])
    return merged


def missing_gaps(ledger,e,sign,amin,amax,dmin,dmax):
    return [d for d in range(dmin,dmax+1)
            if not any(lo<=amin and hi>=amax for lo,hi in intervals(ledger,e,d,sign))]


def summary(ledger):
    groups=defaultdict(list)
    for e,d,sign in sorted({key(r) for r in cells(ledger)}):
        for lo,hi in intervals(ledger,e,d,sign):groups[(e,sign,lo,hi)].append(d)
    rectangles=[]
    for (e,sign,lo,hi),ds in sorted(groups.items()):
        start=end=ds[0]
        for d in ds[1:]+[None]:
            if d==end+1:end=d
            else:
                rectangles.append({'e':e,'sign':sign,'delta_min':start,'delta_max':end,
                                   'abs_a_min':lo,'abs_a_max':hi,'c_coverage':'complete admissible c; see exact enumerated and algebraically excluded intervals in receipts'})
                start=end=d
    return {'high_height_cells':len(cells(ledger)),
            'high_height_exact_trials':sum(integer(x['trials']) for x in ledger['experiments']),
            'high_height_exact_lookups':sum(integer(x['exact_lookups']) for x in ledger['experiments']),
            'rectangles':rectangles,
            'full_height_censuses':ledger.get('full_height_censuses',[]),
            'meaning':'Only admitted finite scopes. Algebraic exclusions are not enumerated trials; calibration and external reports are separate.'}


def certified_addition(baseline, record, output, expected, controller, *, experiment_id='P17'):
    if experiment_id not in ('P17','P18','P19'):
        raise ValueError('unsupported reviewed experiment identity')
    if record['schema']!=f'E5-DISCOVERY-{experiment_id}-v1' or record['source']!=source_identity():
        raise ValueError('foreign experiment source/schema')
    if record['controller_sha256']!=sha(Path(controller).read_bytes()) or record['receipt_verifier_sha256']!=sha((ROOT/'tools/search_discovery_frontier.py').read_bytes()):
        raise ValueError('foreign controller/verifier')
    if record['coverage_ledger_sha256']!=sha(Path(__file__).read_bytes()) or record['prior_coverage_index_sha256']!=sha(canonical(baseline)):
        # Baseline in this workflow is canonicalized JSON for a reproducible hash.
        raise ValueError('foreign ledger code or baseline')
    observed=[x['scope'] for x in record['cells']]
    if observed!=expected:raise ValueError('incomplete or reordered declared territory')
    assert_fresh(baseline,expected)
    total_trials=total_lookups=0;witnesses=[];rows=[]
    for scope,row in zip(expected,record['cells']):
        # Reconstruct exact bounds rather than trusting an externally supplied bbox.
        if scope!=plan(scope['e'],scope['delta'],scope['a_cap'],scope['c_width'],scope['a_min'],scope['sign'],scope.get('bound_mode')=='two_term'):
            raise ValueError('noncanonical finite c coverage')
        folder=output/cell_id(scope)
        accepted=verify_cell(folder,scope,replay=False)
        if sha((folder/'accepted.json').read_bytes())!=row['receipt_sha256'] or row['totals']!=accepted['totals'] or row['witnesses']!=accepted['witnesses']:
            raise ValueError('parent/child receipt mismatch')
        total_trials+=accepted['totals']['trials'];total_lookups+=accepted['totals']['exact_lookups'];witnesses.extend(accepted['witnesses'])
        rows.append({'e':scope['e'],'delta':scope['delta'],'sign':scope['sign'],
                     'abs_a_min':scope['a_min'],'abs_a_max':scope['a_cap'],
                     'c_min':scope['c_min'],'c_max':scope['c_max'],
                     'legacy_c_min':scope.get('legacy_c_min',scope['c_min']),
                     'algebraically_excluded_c_values':scope.get('algebraically_excluded_c_values',0),
                     'trials':accepted['totals']['trials'],'exact_lookups':accepted['totals']['exact_lookups'],
                     'primitive_witnesses':accepted['totals']['primitive_witnesses'],
                     'receipt_sha256':row['receipt_sha256']})
    if total_trials!=record['total_trials'] or total_lookups!=record['total_exact_lookups'] or witnesses!=record['witnesses']:
        raise ValueError('aggregate count/witness mismatch')
    return {'id':experiment_id,'status':'native_and_independent_full_replay_accepted',
            'prior_coverage_index_sha256':sha(canonical(baseline)),
            'source':record['source'],'receipt_sha256':sha(canonical(record)),
            'trials':total_trials,'exact_lookups':total_lookups,'primitive_witnesses':len(witnesses),
            'witnesses':witnesses,'cells':rows,
            'meaning':'Complete restricted cells only; archive publication metadata is recorded separately.'}


def append(ledger, addition):
    if addition.get('status')!='native_and_independent_full_replay_accepted' or addition.get('prior_coverage_index_sha256')!=sha(canonical(ledger)):
        raise ValueError('unverified addition or foreign predecessor ledger')
    if (sum(integer(r['trials']) for r in addition['cells'])!=addition['trials'] or
        sum(integer(r['exact_lookups']) for r in addition['cells'])!=addition['exact_lookups'] or
        sum(integer(r['primitive_witnesses']) for r in addition['cells'])!=addition['primitive_witnesses'] or
        len(addition['witnesses'])!=addition['primitive_witnesses']):
        raise ValueError('addition totals do not match admitted cells')
    result=copy.deepcopy(ledger)
    if any(x['id']==addition['id'] for x in result['experiments']):raise ValueError('experiment already logged')
    scopes=[{'e':x['e'],'delta':x['delta'],'sign':x['sign'],'a_min':x['abs_a_min'],'a_cap':x['abs_a_max']} for x in addition['cells']]
    assert_fresh(result,scopes)
    result['experiments'].append(addition)
    result['coverage_summary']=summary(result)
    return result


def markdown(ledger):
    s=summary(ledger)
    lines=['# Accepted Euler search territory','',
           '| e | First term | delta | abs(a) | c coverage |',
           '| ---: | --- | --- | --- | --- |']
    for r in s['rectangles']:
        ds=str(r['delta_min']) if r['delta_min']==r['delta_max'] else f"{r['delta_min']}..{r['delta_max']}"
        lines.append(f"| {r['e']:,} | {r['sign']} | {ds} | {r['abs_a_min']}..{r['abs_a_max']} | complete admissible c |")
    lines+=['',f"High-height exact (c,abs(a)) trials: **{s['high_height_exact_trials']:,}**. Historical repeats and calibration tests are excluded from this total.",
            '', 'Exact enumerated c intervals, algebraic exclusions, source hashes and resources remain in each experiment receipt. This table does not assert full target-height coverage.','']
    for c in s['full_height_censuses']:
        lines.append(f"Full strictly positive height census: e={c['e_min']}..{c['e_max']}, independent replay accepted; evidence: {c.get('archive',c.get('evidence_document','source record'))}.")
    lines+=['','Calibration-only domains and externally reported searches are listed separately in the JSON ledger.','']
    return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser();p.add_argument('--ledger',type=Path,required=True);p.add_argument('--markdown',action='store_true')
    args=p.parse_args();x=json.loads(args.ledger.read_bytes())
    print(markdown(x) if args.markdown else canonical(summary(x)).decode('ascii'),end='')

if __name__=='__main__':main()
