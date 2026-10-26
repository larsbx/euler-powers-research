# Accepted Euler search evidence

Start with [TERRITORY.md](TERRITORY.md), generated from the cumulative ledger.
[current.json](current.json) selects [index-p19.json](index-p19.json) and binds
its exact SHA256. This records all accepted high-height cells, the complete
positive B320 census, test-covered calibration domains, historical subsets,
failed attempts and unreproduced external reports as distinct categories.

The high-height total is **2,441,336,576 disjoint exact (c,abs(a)) trials** in
63 cells. B320 uses a different trial unit and is not added to that count.
Algebraically excluded c prefixes are not enumerated trials. Plans, interrupted
runs, old regressions and calibration-only checks receive no new territory credit.

Every experiment retains its raw ZIP, source-bound receipts, timing reports,
run/source identity and integrity digests. B320's 80 shards have their own
archive and full root crosscheck. Calibration-only evidence has separate source
and validation-log pointers. Exact original archive/receipt bytes are retained.

[index.json](index.json), [index-p16.json](index-p16.json) and [index-p17.json](index-p17.json) and [index-p18.json](index-p18.json) remain unchanged
because accepted later experiments hash them as predecessor inputs. Their
remaining-work examples describe historical stopping points; use the current
pointer for the accepted union. Replaying a historical experiment requires its
recorded source snapshot and predecessor, not the current union.

No listed high-height block is a complete target-height or general signed
census. Zero primitive witnesses in a restricted cell does not imply global
nonexistence. See [P19](../../docs/POST_BRAUN_P19.md) for observed results and
[coverage_ledger.py](../../tools/coverage_ledger.py) for overlap/admission rules.

Exact algebra and pair-query conformance are inventoried separately under `data/algebra` and receive zero discovery trial credit.

P19 production-stripe comparisons and the superseded-source repeat have their own source-bound records and zero duplicate discovery credit. Selected positive and supported signed first-term magnitudes now extend through 4096.
