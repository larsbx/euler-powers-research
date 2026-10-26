# Accepted Euler search territory

| e | First term | delta | abs(a) | c coverage |
| ---: | --- | --- | --- | --- |
| 2,760,001 | negative | 64 | 1..256 | complete admissible c |
| 2,760,001 | negative | 4 | 1..1024 | complete admissible c |
| 2,760,001 | negative | 16 | 1..1024 | complete admissible c |
| 2,760,001 | positive | 1..32 | 1..1024 | complete admissible c |
| 2,760,001 | positive | 64 | 1..1024 | complete admissible c |
| 2,760,001 | positive | 256 | 1..1024 | complete admissible c |
| 2,760,002 | positive | 1..3 | 1..64 | complete admissible c |
| 2,760,003 | positive | 1..3 | 1..64 | complete admissible c |

High-height exact (c,abs(a)) trials: **1,716,786,944**. Historical repeats and calibration tests are excluded from this total.

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
the 1,716,786,944 high-height trial total. Original validation logs and source
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
