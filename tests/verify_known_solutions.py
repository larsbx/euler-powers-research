"""Reproduce integer identities, primitivity, and universal elementary sieves.

This is a check of the included data, NOT an exhaustive solution search.
Run: python3 tests/verify_known_solutions.py
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "known_solutions.csv"


def verify_row(row: dict[str, str]) -> None:
    values = tuple(int(row[key]) for key in "abcde")
    assert sum(x**5 for x in values[:4]) == values[4] ** 5, values
    assert math.gcd(*values) == 1, values
    assert (all(x > 0 for x in values)) == (row["all_positive"] == "true")
    for prime in (5, 11):
        assert sum(x % prime == 0 for x in values) in (1, 3), (prime, values)


def verify_modular_lemmas() -> None:
    assert {pow(x, 5, 11) for x in range(11)} == {0, 1, 10}
    assert {pow(x, 5, 25) for x in range(25)} == {0, 1, 7, 18, 24}


def main() -> None:
    verify_modular_lemmas()
    with DATA.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 4
    for row in rows:
        verify_row(row)
    assert sum(row["all_positive"] == "true" for row in rows) == 2
    print(f"Verified {len(rows)} primitive identities; 2 have all positive summands.")


if __name__ == "__main__":
    main()
