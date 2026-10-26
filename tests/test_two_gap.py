"""Independent exhaustive small pair oracle and signed calibration controls."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from search_two_gap import reconstruct,oracle,validate,plan


def main():
    checked=0
    for h in range(1,9):
        pairs={(r+h)**5-r**5:r for r in range(1,65)}
        targets={-1,0,1}
        for q in pairs:targets.update((q-1,q,q+1))
        for q in sorted(targets):
            got=reconstruct(q,h)
            # Neighboring targets can represent a pair outside this tiny box;
            # compare complete finite box membership in both directions.
            assert (got if got is not None and got<=64 else None)==pairs.get(q)
            if got is not None:assert got>0 and (got+h)**5-got**5==q
            checked+=1
    _,counts,hits=oracle([1956878,665,9010,719114,719116])
    assert len(hits)==1 and hits[0]==[1,719115,1331622,1340632,1331622,1956213,1956878,1]
    assert counts[0]==6 and counts[8]==1
    for cell in ([24,1,1,1,23],[24,23,23,1,23],[100,2,3,97,99]):
        raw,counts,hits=oracle(cell)
        assert not hits
    assert len(plan())==160 and len({tuple(x) for x in plan()})==160
    for cell in plan():validate(cell)
    print(f'{checked} exact pair/neighbor reconstruction controls and Braun calibration passed; tests add no discovery coverage.')


if __name__=='__main__':main()
