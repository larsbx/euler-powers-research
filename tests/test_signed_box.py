"""Independent brute-force, finite-domain, normalization and native refusals."""
from itertools import combinations_with_replacement
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from search_signed_box import ROOT, magnitudes, partition, check_partition, oracle, output_hits, publish
from primitive_candidates import analyze, signature


def refused(f):
    try:f()
    except ValueError:return
    raise AssertionError('invalid input accepted')


def main():
    for n,small,start in [(1,1,1),(4,4,1),(5,2,19),(6,0,3000001)]:
        case=dict(n=n,small=small,start=start);S=magnitudes(n,small,start);xs=sorted([-x for x in S]+S)
        brute=[]
        for terms in combinations_with_replacement(xs,5):
            if terms[2]>0 and sum(x**5 for x in terms)==0 and not any(-x in terms for x in terms):brute.append(terms)
        raw,hits=oracle(case,'index');assert hits==brute==output_hits(raw)
    for n in (1,2,31,128,129,1024):
        parts=partition(n,min(128,n));check_partition(n,parts)
        assert sum(b-a+1 for a,b in parts)==n
    for parts in ([],[(1,3),(3,4)],[(1,2),(4,4)],[(2,4)],[(1,5)],[(1,4),(5,4)]):
        refused(lambda:check_partition(4,parts))
    for args in ((0,0,1),(1025,1,2),(4,5,6),(4,1,1),(4,-1,3),(4,0,10**9+1)):
        refused(lambda:magnitudes(*args))
    known=(-144,27,84,110,133)
    for k in (1,2,-1,-7):assert signature([k*x for x in known])==signature(known)
    for terms in ((-1,1,2,3,4),(0,27,84,110,-144),(27,84,110,133,-145)):
        refused(lambda:analyze(dict(schema='E5-CANDIDATE-PROPOSAL-v1',method='regression',provenance='adversarial',terms=list(map(str,terms)))))
    with tempfile.TemporaryDirectory() as tmp:
        folder=Path(tmp)
        with patch('search_signed_box.verify',side_effect=ValueError('incomplete native rows')):
            refused(lambda:publish(folder,{'provisional':'test'}))
        assert (folder/'pending.json').exists() and not (folder/'accepted.json').exists()
    with tempfile.TemporaryDirectory() as tmp:
        folder=Path(tmp)
        with patch('search_signed_box.verify') as replay:
            publish(folder,{'provisional':'test'})
            replay.assert_called_once_with(folder,'pending.json')
        assert (folder/'accepted.json').exists() and not (folder/'pending.json').exists()
    with tempfile.TemporaryDirectory() as tmp:
        binary=Path(tmp)/'signed'
        subprocess.run(['mojo','build','-I','kernel','-I','algebra','-I','.deps/finite-math-kernels/kernel','discovery/signed_box.mojo','-o',str(binary)],cwd=ROOT,check=True,timeout=300)
        for case in (dict(n=8,small=8,start=1),dict(n=8,small=4,start=3000001)):
            n=case['n'];args=[str(binary),'index',str(n),'1',str(n),str(case['small']),str(case['start'])]
            assert subprocess.check_output(args)==oracle(case,'index')[0]
        for args in (['index','0','1','1','0','1'],['index','1025','1','1','1','2'],
                     ['index','8','2','1','8','1'],['index','8','1','9','8','1'],
                     ['index','8','1','8','4','4'],['reconstruct','8','1','8','4','100'],
                     ['reconstruct','33','1','33','33','1'],['float','8','1','8','8','1']):
            r=subprocess.run([str(binary),*args],capture_output=True)
            assert r.returncode!=0 and b'COMPLETE' not in r.stdout
    print('P21 brute-force, band, shard, equivalence, arithmetic and native refusal regressions passed')
if __name__=='__main__':main()
