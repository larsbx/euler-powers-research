# P4 — Exact digit-sum / CRT residue pruning

## Shared kernel vs Euler search

Generic exact arithmetic belongs in `larsbx/finite-math-kernels`:
`finite_polynomial.pair_power_residue.PairPowerResiduePrefix`,
`decimal_digit_sum`, and `decimal_alternating_sum`.
The upstream module uses the canonical `Modulus` ring, not floating
point, and maintains the **complete** set

`R_m(c) = { a^5 + b^5 (mod m) : 1 <= a <= b <= c }`.

At step `c`, `advance()` adds every `(a,c)` pair, including
`(c,c)`. The set is mathematically monotone and retains each distinct
residue regardless of fifth-power collisions. A query is a necessary
condition for an exact ordered left pair, **never evidence of a solution**.

The Euler-specific search adds the shared prefix sieve in
`kernel/pair_partition.mojo` after exact signed-complement positivity
and partition ownership accounting, but before the expensive exact-sum
packed-index lower bound. It advances the table once per outer
`c` under each target height `e`. It reuses the existing
`B<=144`, partition-modulus `1<=M<=35`, checked Int64 arithmetic
and immutable upstream dependency pin. The additional digit-sum
modulus is always `2475` and is **independent of partition M**.

Decimal arithmetic gives `n ≡ digit_sum(n) (mod 9)`,
`n ≡ alternating_digits(n) (mod 11)`, while `n mod 25` depends only
on its final two decimal digits. Because 9, 11 and 25 are pairwise
coprime, their combined exact ring is `Z/2475Z` by CRT.
The shared power-residue table avoids repeatedly scanning digits in
the hot loop: a modular exponentiation/canonical table check suffices.
No assumption about independence of bounded search distributions is made.

## Soundness, output invariants and evidence

`DigitSumPruning.lean` proves that every valid positive primitive E5
solution passes the **prefix** at its own `c`, not just the looser
height-wide left-pair image previously proved by `PrimePowerSieve`.
It also proves the contrapositive: absence from the exact residue
prefix implies non-validity. This statement is independent of
primality and applies to the composite modulus 2475.

The search still increments `PART` right-pair visit counters **before**
the new sieve; only the native exact-index lookup is skipped for
impossible complements. The emitted `E5PARTv1` records and pinned
`E5PART-REPLAY-v2` digest do not change. In particular the B144/M35
reference remains 2,574 rows, 475,063 positive-complement visits,
one positive primitive certificate `(27,84,110,133,144)`, and root
`5b8ed68d8512bb11bf4ac57e2f79657e65893427c157c0615b784d86671af482`.

Native Mojo `digit_filter_probe.mojo` measures modular rejection on
the same bounded right pairs. Independent Python `test_digit_filter.py`
uses sets of exact arbitrary-precision fifth-power sums, not the Mojo
bitset structure. It tests three domains (B=8,48,144) and five moduli.
For B=144, the verified reference counts are:

| Modulus | Rejected of 475,063 positive right pairs | Retained |
| --- | ---: | ---: |
| 9 | 21,873 | 453,190 |
| 11 | 152,879 | 322,184 |
| 25 | 133,804 | 341,259 |
| 99 | 181,825 | 293,238 |
| **2475** | **356,770** | **118,293** |

The actual witness complement is 1881 modulo 2475, present in
`R_2475(110)`; any filter that rejects it is incorrect.

**These are candidate-rejection counts, not wall-clock improvement.**
Since P3 exact lookups are already fast, the extra table construction
could outweigh saved lookups. The benchmark in
`tests/benchmark_digit_filter.py` compiles the historical unfiltered
P3 native source at commit
`d42cfa6a81a76dd8db973c92dc6efa5b6e518690` and the new
filtered native source with **the same toolchain and shared library
pin**. It uses B=48/144, M=35, alternating-order repeated trials,
GNU-time wall/RSS readings, and **requires identical exact stream,
Python oracle and SHA root before recording numbers**. CI retains the
raw JSON artifact `native-digit-filter-benchmark`.

## Reproduce

```sh
pixi run --locked verify-research
bash tools/verify-formal.sh
pixi run --locked python tests/benchmark_digit_filter.py \
  --output benchmarks/results/digit-filter-comparison.json
```

Limitations: only ordered positive bounded E5 candidates are filtered;
no wider census, signed/zero solution claim, unbounded completeness,
published exhaustive-search reproduction, cryptographic run
authenticity or Euler conjecture resolution is established.
