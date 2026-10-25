"""Exact modulus-frontier selection for the existing B=144 positive search.

The upstream reusable kernel supplies correct membership; this script is
Euler-specific empirical evidence of rejected right pairs, NOT a proof of
integer nonexistence, and makes no runtime-speedup inference.
"""
from __future__ import annotations

from test_digit_filter import oracle

MODULI = (9, 11, 25, 99, 125, 225, 275, 495, 625, 825, 891, 1089,
          1375, 1485, 2475, 3025, 4455, 4950, 7425, 9075,
          12375, 22275, 24750, 27225, 37125, 49500, 74250, 99000)
KNOWN_REJECTED = {
    9: 21873, 11: 152879, 25: 133804, 99: 181825,
    2475: 356770, 99000: 465238,
}


def main():
    records = []
    for modulus in MODULI:
        count, rejected = oracle(144, modulus)
        assert count == 475063
        if modulus in KNOWN_REJECTED:
            assert rejected == KNOWN_REJECTED[modulus], modulus
        records.append((modulus, rejected))
    assert records[-1] == (99000, 465238)
    assert 99000 % 2475 == 0
    assert 99000 == 9 * 11 * 1000
    assert 465238 - 356770 == 108468
    print("MODULUS rejected retained dense_table_bytes")
    for modulus, rejected in records:
        print(modulus, rejected, 475063 - rejected, modulus)
    print("B144 full CRT refinement 99000 rejects 465238/475063 "
          "(97.932%, vs 75.099% at 2475); 9825 remain.")


if __name__ == "__main__":
    main()
