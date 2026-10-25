# P5: exact decimal CRT modulus frontier (99,000)

## Algebraic refinement

Modulo 9, the decimal digit sum determines the residue. Modulo 11,
the alternating units-first digit sum determines the residue. Modulo
1000, the last three decimal digits determine the residue.

These moduli are pairwise coprime, so the full combined ring is

`Z/99000Z = Z/(9*11*1000)Z` as a CRT product.

The upstream shared Mojo `PairPowerResiduePrefix` computes the
**complete** set `{a^5+b^5 mod 99000 : 1<=a<=b<=c}` for each
current ordered prefix `c`. The positive Euler search only discards
a complement `t=e^5-c^5-d^5>0` when this exact set does not contain
`t mod 99000`. The existing Lean `valid_digit_prefix` and
`missing_digit_prefix_rejects` theorems quantify over **every
modulus**, thus already cover 99000. The modular condition remains
necessary, not sufficient.

Because 2475 divides 99000 (factor 40), any complement accepted by
the 99000 prefix also passes the 2475 prefix. This is an exact
refinement of the P4 filter; no probabilistic independence of
bounded integer residues is asserted.

## B=144 exhaustive prefilter comparisons

The independent `tests/modulus_frontier.py` scans the very same
475,063 strictly positive `(c,d,e)` complements as the native
search and derives sets with Python arbitrary-precision fifth powers.
It benchmarks a declared finite modulus portfolio, including
9,11,25,99,125,225,275,495,625,825,891,1089,1375,1485,2475,
3025,4455,4950,7425,9075,12375,22275,24750,27225,37125,
49500,74250,99000 (all <=100000). Each finite candidate-sweep
count is empirical bounded computation, not an asymptotic theorem.

| Modulus | Rejected | Surviving | % rejected |
|---:|---:|---:|---:|
| 9 | 21,873 | 453,190 | 4.60% |
| 11 | 152,879 | 322,184 | 32.18% |
| 25 | 133,804 | 341,259 | 28.17% |
| 99 | 181,825 | 293,238 | 38.27% |
| 2475 | 356,770 | 118,293 | 75.10% |
| 99000 | **465,238** | **9,825** | **97.93%** |

The 99000 prefix rejects **108,468 additional** right-pair visits
relative to the old 2475 prefix. The known Lander–Parkin solution
still survives because
`144^5-110^5-133^5 ≡ 27^5+84^5 ≡ 56331 (mod 99000)`.

**Critical distinction:** the visit counter is still incremented for
every positive complement before the rejection test, so PART counts
stay at 475,063 and the exact E5PARTv1 canonical root must remain
`5b8ed68d8512bb11bf4ac57e2f79657e65893427c157c0615b784d86671af482`
with 2,574 rows and one primitive certificate.

## Resource and timing evidence

The dense shared filter uses `m` Boolean membership entries plus up
to `c+1` power entries and allocator/runtime overhead. At 99000,
this is 40 times as many Boolean entries as 2475. The filter is
rebuilt for each target height, while the exact index is independently
rebuilt for each height. A larger modulus can reject more candidates
yet still slow total execution because of initialization and cache
effects; **97.93% is not a runtime speedup percentage**.

`tests/benchmark_modulus_selection.py` compiles merged P4
(`5de9573ab831f2a1e47cbb1efd0c089f1aa253c8`) versus the
current P5 binary with the *same toolchain and shared library pin*.
It executes alternating-order paired samples at B=48 and B=144,
M=35 with seven repetitions. Every raw native stream must match
the independent oracle and the pinned SHA root. The benchmark records
process-inclusive monotonic nanosecond elapsed time and GNU time
wall/RSS, plus Git source SHA-256, commit identity, platform and
toolchain. CI preserves a JSON `native-modulus-selection` artifact.
No generalized performance claim is made from small hosted-runner
samples.

## Verification and scope

```sh
pixi run --locked python tests/modulus_frontier.py
pixi run --locked verify-research
pixi run --locked python tests/benchmark_modulus_selection.py
bash tools/verify-formal.sh
```

At the original P5 milestone, the executable accepted only `2<=B<=144`, `1<=M<=35` for
partitioning, regardless of the much larger *independent* CRT filter
modulus. The historical output, checked Int64 packing radix 145,
signed known-solution corpus, and formal obligations are unchanged.
Increasing B requires a separately reviewed packed representation
size argument and proof; BigZ by itself does not establish a wider
compiled search. No new positive solution or Braun-range reproduction
is claimed.
