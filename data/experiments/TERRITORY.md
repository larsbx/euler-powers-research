# Accepted Euler search territory

The near-cancellation map below and the P20 signed two-gap map at the end
use different parameterizations and trial units. Both are finite coverage
statements; their iteration totals are not added.

| e | First term | delta | abs(a) | c coverage |
| ---: | --- | --- | --- | --- |
| 2,760,001 | negative | 64 | 1..256 | complete admissible c |
| 2,760,001 | negative | 16 | 1..1024 | complete admissible c |
| 2,760,001 | negative | 4 | 1..4096 | complete admissible c |
| 2,760,001 | positive | 5..7 | 1..1024 | complete admissible c |
| 2,760,001 | positive | 9..15 | 1..1024 | complete admissible c |
| 2,760,001 | positive | 17..32 | 1..1024 | complete admissible c |
| 2,760,001 | positive | 64 | 1..1024 | complete admissible c |
| 2,760,001 | positive | 256 | 1..1024 | complete admissible c |
| 2,760,001 | positive | 1..4 | 1..4096 | complete admissible c |
| 2,760,001 | positive | 8 | 1..4096 | complete admissible c |
| 2,760,001 | positive | 16 | 1..4096 | complete admissible c |
| 2,760,002 | positive | 1..3 | 1..64 | complete admissible c |
| 2,760,003 | positive | 1..3 | 1..64 | complete admissible c |

High-height exact (c,abs(a)) trials: **2,441,336,576**. Historical repeats and calibration tests are excluded from this total.

Exact enumerated c intervals, algebraic exclusions, source hashes and resources remain in each experiment receipt. This table does not assert full target-height coverage.

Full strictly positive height census: e=2..320, independent replay accepted; evidence: [original B320 ZIP](b320-run-40334880431.zip).

Calibration-only domains and externally reported searches are listed separately in the JSON ledger.

## Test-covered scopes (separate evidence class)

| e | First term | delta | abs(a) | c | Result |
| ---: | --- | ---: | --- | --- | --- |
| 144 | positive | 11 | 1..64 | 93..115 | known primitive witness |
| 85,359 | positive | 77 | 1..64 | 23255..28969 | known primitive witness |
| 85,360 | positive | 77 | 1..64 | 23255..28969 | zero primitive witnesses |
| 14,132 | negative | 64 | 1..256 | 5758..6613 | known primitive witness |

These scopes passed native/Python test comparisons. Their evidence class is
kept separate from source-bound discovery-cell receipts; none is credited to
the 2,441,336,576 high-height trial total. Original validation logs and source
locations are recorded in [the JSON ledger](index-p17.json). Earlier B12/B144/
B256 searches are subsumed by B320; P13's first cell is subsumed by P14.

Published million-height search claims are external reports and are not
accepted territory of this repository. Unlisted gaps, larger first summands,
other high target heights and general signed orderings remain open.

The four known registry identities also have native BigZ/Python point checks,
including the Braun signed identity outside the smallest-negative-term search
ordering. These are point verifications, not additional searched blocks or
new discoveries; the JSON ledger preserves their exact tuples and provenance.


Exact cyclotomic and signed pair reconstruction conformance is recorded separately in `data/algebra`; it contributes zero Euler discovery cells.

Production residue-first benchmarks and the superseded P19 run are inventoried separately and receive zero duplicate discovery credit. P19 extends selected positive and supported signed minimum summands through 4096; other gaps and general signed orderings remain open.

## P20 signed two-gap territory

The [separate signed ledger](index-p20-signed-two-gap.json) and
[hashed pointer](signed-two-gap-current.json) record 160 cells (320 orientations).

| parameter | exact declared values |
|---|---|
| e | 1956877, 1956878, 1956879, 2760001, 3000001 |
| delta=e-d | 64, 665, 4096, 16384 |
| h=abs(c-u) | 64, 1024, 9010, 16384 |
| b | 65537..131072; 524289..589824 |
| orientation 0 | u=r,c=r+h; b+1<=r<=e-delta-h |
| orientation 1 | c=r,u=r+h; b<=r<=min(e-delta,e-1-h) |

All admissible r in each listed cell are covered by exact inversion of a
strictly increasing fifth-power difference. There are 20,971,520 exact
b/orientation trials and zero identities. This domain has u>b and is disjoint
from the old signed u<=b cells. The [accepted receipt](two-gap-40421394757-accepted.json)
preserves original native artifacts and complete independent Python replay.

Every undeclared e/delta/h/b, u=b, u=c, u>=e, two negative input summands and
complete target-height coverage remain unsearched by this experiment.
Braun calibration and all repeated workflows get zero new coverage credit.
No new primitive or global nonexistence claim follows from this finite result.
