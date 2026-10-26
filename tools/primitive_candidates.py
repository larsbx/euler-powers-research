"""Exact rational proposal normalization and generic signed primitive admission.

This tool never announces a discovery. An absent registry class is a candidate
for current literature review, even after native/Python arithmetic agreement.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
from math import gcd,lcm
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from hashlib import sha256

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/'data/literature/known_primitive_e5_2026-10-26.json'
PIN='c5b2d3d7879bcf2354d4d9784bd20a6b3dc610fd'
TOKEN=re.compile(r'-?(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?\Z',re.ASCII)
SOURCES=('tools/primitive_candidates.py','discovery/verify_candidate.mojo',
         'data/DISCOVERY_CHARTER.json','data/literature/known_primitive_e5_2026-10-26.json',
         'scripts/run_mojo.sh','pixi.toml','pixi.lock')


def canonical(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode('ascii')
def sha(x):return sha256(x).hexdigest()


def signature(terms):
    if len(terms)!=5 or any(type(x) is not int or x==0 for x in terms):
        raise ValueError('exactly five nonzero integer terms required')
    g=gcd(*terms)
    reduced=tuple(x//g for x in terms)
    return min(tuple(sorted(reduced)),tuple(sorted(-x for x in reduced)))


def registry_classes():
    registry=json.loads(REGISTRY.read_bytes())
    result={}
    for row in registry['records']:
        terms=tuple(row['summands'])+(-row['target'],)
        if sum(x**5 for x in terms)!=0 or gcd(*terms)!=1:
            raise ValueError('invalid pinned known-identity registry')
        key=signature(terms)
        if key in result:raise ValueError('duplicate registry class')
        result[key]=row['id']
    return result


def analyze(proposal,known=None):
    if proposal.get('schema')!='E5-CANDIDATE-PROPOSAL-v1':
        raise ValueError('unsupported candidate proposal schema')
    for k in ('method','provenance'):
        if type(proposal.get(k)) is not str or not proposal[k].strip() or len(proposal[k])>4096:
            raise ValueError('candidate method and provenance are required')
    terms=proposal.get('terms')
    if type(terms) is not list or len(terms)!=5:
        raise ValueError('exactly five zero-sum terms required')
    rationals=[]
    for token in terms:
        if type(token) is not str or not TOKEN.fullmatch(token):
            raise ValueError('candidate terms require canonical signed rational strings')
        parts=token.split('/')
        if any(len(x.lstrip('-'))>128 for x in parts):
            raise ValueError('rational proposal exceeds 128-digit component resource cap')
        x=Fraction(token)
        if x==0:raise ValueError('zero terms are excluded')
        rationals.append(x)
    denominator=lcm(*(x.denominator for x in rationals))
    cleared=tuple(x.numerator*(denominator//x.denominator) for x in rationals)
    if any(-x in cleared for x in cleared):
        raise ValueError('cancelling opposite terms are excluded')
    if sum(x**5 for x in cleared)!=0:
        raise ValueError('candidate does not satisfy the exact fifth-power equation')
    common=gcd(*cleared)
    primitive=tuple(x//common for x in cleared)
    if sum(x**5 for x in primitive)!=0 or gcd(*primitive)!=1:
        raise ValueError('primitive normalization failed exact verification')
    sig=signature(primitive)
    largest=max(primitive,key=abs)
    oriented=primitive if largest<0 else tuple(-x for x in primitive)
    e=abs(largest);summands=list(oriented);summands.remove(-e);summands.sort()
    known=registry_classes() if known is None else known
    known_id=known.get(sig)
    return {'schema':'E5-CANDIDATE-ANALYSIS-v1','proposal':proposal,
            'denominator_lcm':str(denominator),'cleared_integer_terms':list(map(str,cleared)),
            'cleared_integer_gcd':str(common),'input_integer_tuple_primitive':common==1,
            'primitive_terms':list(map(str,primitive)),'canonical_class':list(map(str,sig)),
            'presentation':{'summands':list(map(str,summands)),'target':str(e),
                            'domain':'strictly_positive' if all(x>0 for x in summands) else 'signed',
                            'strict_largest_target':all(abs(x)<e for x in summands)},
            'known_id':known_id,'status':'known_class' if known_id else 'candidate_requires_current_literature_review',
            'native_verified':False,'discovery_claim':False,
            'remaining_obligations':[] if known_id else ['independent native arithmetic','current primary-source literature/equivalence review','inspectable derivation/search provenance']}


def expected_native(terms):
    ints=tuple(map(int,terms))
    return f"RESULT E5-CANDIDATE-v1 {sum(x**5 for x in ints)} {gcd(*ints)} {int(all(x!=0 for x in ints))}\n".encode('ascii')


def verify_native(analysis,binary):
    # Bind every arithmetic/classification field to a fresh exact analysis;
    # native agreement on an attacker-modified nonzero residual is not
    # candidate acceptance, and caller-supplied labels carry no authority.
    fresh=analyze(analysis['proposal'])
    if analysis!=fresh:
        raise ValueError('modified or foreign candidate analysis')
    analysis=fresh
    outputs={}
    for label in ('cleared_integer_terms','primitive_terms'):
        terms=analysis[label]
        r=subprocess.run([str(binary),*terms],capture_output=True,timeout=60)
        if r.returncode or r.stdout!=expected_native(terms):
            raise ValueError('native candidate verification failed: '+r.stderr.decode(errors='replace'))
        outputs[label]=r.stdout.decode('ascii')
    result=dict(analysis);result['native_verified']=True
    result['remaining_obligations']=[x for x in result['remaining_obligations'] if x!='independent native arithmetic']
    # Absence from a snapshot is never a discovery certificate.
    return result,outputs


def source_hashes():return {p:sha((ROOT/p).read_bytes()) for p in SOURCES}


def compile_verifier(binary):
    pin=subprocess.check_output(['git','-C',str(ROOT/'.deps/finite-math-kernels'),'rev-parse','HEAD'],text=True).strip()
    if pin!=PIN:raise ValueError('foreign arithmetic dependency')
    r=subprocess.run(['mojo','build','-I','.deps/finite-math-kernels/kernel',
                      'discovery/verify_candidate.mojo','-o',str(binary)],cwd=ROOT,capture_output=True,timeout=300)
    if r.returncode:raise ValueError(r.stderr.decode())


def main():
    p=argparse.ArgumentParser();p.add_argument('proposal',type=Path);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    proposal_bytes=args.proposal.read_bytes();analysis=analyze(json.loads(proposal_bytes))
    # Native toolchain is available through pixi; initialize the pinned package
    # first with pixi run --locked verify. No shell or credential discovery here.
    with tempfile.TemporaryDirectory(prefix='e5-candidate-') as tmp:
        binary=Path(tmp)/'verify';compile_verifier(binary);result,outputs=verify_native(analysis,binary)
    folder=args.output.resolve();folder.mkdir(parents=True,exist_ok=False)
    (folder/'proposal.json').write_bytes(proposal_bytes)
    for name,text in outputs.items():(folder/(name+'.txt')).write_text(text,encoding='ascii')
    receipt={'schema':'E5-CANDIDATE-RECEIPT-v1','analysis':result,'sources':source_hashes(),
             'proposal_sha256':sha(proposal_bytes),'native_stdout_sha256':{k:sha(v.encode()) for k,v in outputs.items()},
             'finite_math_kernels_pin':PIN,'source_commit':os.getenv('GITHUB_SHA'),'workflow_run_id':os.getenv('GITHUB_RUN_ID')}
    (folder/'receipt.json').write_bytes(canonical(receipt))
    print(result['status']+'; primitive normalization independently native/Python verified; discovery_claim=false')


if __name__=='__main__':main()
