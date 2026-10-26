"""Exact equivalence/normalization, no-false-discovery and native intake probes."""
import argparse
from fractions import Fraction
from itertools import permutations
import json
from pathlib import Path
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import primitive_candidates as candidate_module
from primitive_candidates import (ROOT,PIN,REGISTRY,analyze,canonical,signature,
                                registry_classes,compile_verifier,verify_native,
                                expected_native,source_hashes,sha)


def proposal(terms):
    return {'schema':'E5-CANDIDATE-PROPOSAL-v1','terms':list(map(str,terms)),
            'method':'candidate intake conformance','provenance':'known registry transformations, not new discoveries'}


def corpus():
    out=[]
    for row in json.loads(REGISTRY.read_bytes())['records']:
        terms=tuple(row['summands'])+(-row['target'],)
        for scale in (Fraction(1),Fraction(7),Fraction(1,7),Fraction(-11),Fraction(10**80,13)):
            out.append(proposal([scale*x for x in terms]))
    return out


def refused(f):
    try:f()
    except ValueError:return
    raise AssertionError('invalid candidate accepted')


def python_checks():
    charter=json.loads((ROOT/'data/DISCOVERY_CHARTER.json').read_bytes())
    assert charter['registry_absence_is_discovery'] is False and charter['current_discovery_claim'] is False
    assert 'general_signed_nonzero_integer' in charter['domains']
    known=registry_classes();rows=json.loads(REGISTRY.read_bytes())['records'];count=0
    for row in rows:
        terms=tuple(row['summands'])+(-row['target'],)
        key=signature(terms)
        for order in permutations(terms):
            for scale in (Fraction(1),Fraction(-7),Fraction(1,13)):
                r=analyze(proposal([scale*x for x in order]),known)
                assert r['known_id']==row['id'] and tuple(map(int,r['canonical_class']))==key
                assert not r['native_verified'] and not r['discovery_claim'];count+=1
        # A deliberately empty registry fixture must produce review-required,
        # never a discovery. It is not used by the production CLI or published.
        unknown=analyze(proposal(terms),{})
        assert unknown['status']=='candidate_requires_current_literature_review'
        assert not unknown['discovery_claim'] and 'current primary-source literature/equivalence review' in unknown['remaining_obligations']
    good=proposal([27,84,110,133,-144])
    for terms in ([27,84,110,134,-144],[0,84,110,133,-144],[-1,1,-2,2,3],
                  ['1/0',84,110,133,-144],['01',84,110,133,-144],
                  ['1.0',84,110,133,-144],['NaN',84,110,133,-144],
                  ['1e2',84,110,133,-144],['1/'+('9'*129),84,110,133,-144],
                  [27,84,110,133],['27','84','110','133',-144]):
        r=dict(good);r['terms']=terms;refused(lambda r=r:analyze(r,known))
    bad=dict(good);bad['provenance']='';refused(lambda:analyze(bad,known))
    for field,value in (('primitive_terms',['27','84','110','134','-144']),
                        ('known_id','invented'),('discovery_claim',True),
                        ('status','discovered'),('cleared_integer_gcd','2')):
        forged=analyze(good,known);forged[field]=value
        # Must refuse before attempting to execute this nonexistent binary.
        refused(lambda forged=forged:verify_native(forged,Path('/nonexistent-candidate-verifier')))
    for p in corpus():assert analyze(p,known)['status']=='known_class'
    # A matching HEAD alone cannot attest the arithmetic actually compiled.
    # Exercise clean, modified tracked, staged and untracked sources in a real
    # isolated git checkout without executing Mojo or touching the real pin.
    old_root,old_pin=candidate_module.ROOT,candidate_module.PIN
    try:
        with tempfile.TemporaryDirectory(prefix='candidate-pin-control-') as tmp:
            root=Path(tmp);checkout=root/'.deps/finite-math-kernels';checkout.mkdir(parents=True)
            def git(*args):
                return subprocess.check_output(['git','-C',str(checkout),*args],text=True,stderr=subprocess.DEVNULL).strip()
            git('init');(checkout/'arithmetic.mojo').write_text('original\n');git('add','arithmetic.mojo')
            git('-c','user.name=Exact Test','-c','user.email=exact-test@example.invalid','commit','-m','fixture')
            candidate_module.ROOT=root;candidate_module.PIN=git('rev-parse','HEAD')
            candidate_module.verify_dependency()
            (checkout/'arithmetic.mojo').write_text('modified\n')
            refused(candidate_module.verify_dependency)
            git('add','arithmetic.mojo');refused(candidate_module.verify_dependency)
            git('reset','--hard','HEAD');(checkout/'injected.mojo').write_text('extra\n')
            refused(candidate_module.verify_dependency)
            (checkout/'injected.mojo').unlink();candidate_module.PIN='0'*40
            refused(candidate_module.verify_dependency)
    finally:candidate_module.ROOT,candidate_module.PIN=old_root,old_pin
    return count


def main():
    p=argparse.ArgumentParser();p.add_argument('--python-only',action='store_true');p.add_argument('--output',type=Path);args=p.parse_args()
    count=python_checks()
    if args.python_only:
        assert args.output is None
        print(f'{count} exact permutation/sign/rational-scale cases, corruption controls and no-false-discovery checks passed; no native execution or search coverage.');return
    if args.output is None:p.error('--output required for native conformance')
    folder=args.output.resolve();folder.mkdir(parents=True,exist_ok=False)
    rows=[]
    with tempfile.TemporaryDirectory(prefix='candidate-conformance-') as tmp:
        binary=Path(tmp)/'verify';compile_verifier(binary)
        for i,prop in enumerate(corpus()):
            result,outputs=verify_native(analyze(prop),binary)
            assert result['known_id'] and result['status']=='known_class' and result['native_verified'] and not result['discovery_claim']
            for label,raw in outputs.items():(folder/f'{i:03d}-{label}.txt').write_text(raw,encoding='ascii')
            rows.append({'proposal':prop,'analysis':result,'native_stdout_sha256':{k:sha(v.encode()) for k,v in outputs.items()}})
        # Exercise native invalid identity and zero flags as arithmetic facts,
        # and refuse noncanonical tokens before any receipt could be admitted.
        controls=[['27','84','110','134','-144'],['0','1','-1','2','-2']]
        for i,terms in enumerate(controls):
            run=subprocess.run([str(binary),*terms],capture_output=True,timeout=60)
            assert run.returncode==0 and run.stdout==expected_native(terms)
            (folder/f'control{i}.txt').write_bytes(run.stdout)
        malformed=[]
        for token in ('-0','01','+1','1/0','1.0','9'*1025):
            run=subprocess.run([str(binary),token,'84','110','133','-144'],capture_output=True,timeout=60)
            assert run.returncode!=0
            malformed.append({'token_kind':token if len(token)<10 else '1025-digit integer','exit_code':run.returncode})
    record={'schema':'E5-CANDIDATE-INTAKE-CONFORMANCE-v1','classification':'candidate_intake_conformance_only',
            'discovery_trials':0,'discovery_claim':False,'finite_math_kernels_pin':PIN,
            'sources':source_hashes(),'conformance_test_sha256':sha(Path(__file__).read_bytes()),
            'python_equivalence_cases':count,'proposals':rows,'native_arithmetic_controls':2,
            'native_malformed_controls':malformed}
    (folder/'accepted.json').write_bytes(canonical(record))
    print(f'Native/Python candidate intake accepted: {len(rows)} known-class rational/scaled proposals, {2*len(rows)+2} arithmetic invocations and six malformed refusals; zero discoveries or search coverage.')


if __name__=='__main__':main()
