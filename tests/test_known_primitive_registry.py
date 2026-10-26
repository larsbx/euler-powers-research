"""Review the published nontrivial primitive fifth-power registry.

A record absent from this curated list is a *candidate for literature
investigation*, never proof of a new solution. Canonical zero-sum
signatures collapse positive scalar multiples, permutations and global
sign reversal (equivalent transfers of terms across the equality).

This is an independent exact Python arithmetic check; native Mojo
known-solution verification remains separately required by CI.
"""
from __future__ import annotations

import csv
import json
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/literature/known_primitive_e5_2026-10-26.json"
CSV = ROOT / "data/known_solutions.csv"


def check_identity(summands: tuple[int, ...], target: int) -> None:
    if len(summands) != 4 or target <= 0 or any(x == 0 for x in summands):
        raise ValueError("unsupported nonzero four-term, positive-target convention")
    if sum(x**5 for x in summands) != target**5:
        raise ValueError("not an exact fifth-power identity")


def canonical_class(summands: tuple[int, ...], target: int) -> tuple[int, ...]:
    """Primitive unoriented signed-five-term class of the exact zero sum."""
    check_identity(summands, target)
    signed_zero_sum = (*summands, -target)
    common = gcd(*signed_zero_sum)
    reduced = tuple(x // common for x in signed_zero_sum)
    ordered = tuple(sorted(reduced))
    inverted = tuple(sorted(-x for x in reduced))
    return min(ordered, inverted)


def verify_registry() -> dict:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert registry["schema"] == "e5-known-nontrivial-primitive-census-v1"
    assert registry["reviewed_as_of"] == "2026-10-26"
    rows = registry["records"]
    assert len(rows) == 4
    assert len({r["id"] for r in rows}) == len(rows)
    assert [r["year"] for r in rows] == [1966, 1996, 2004, 2026]
    assert all(r["evidence"] == "exact_integer_identity_and_five_way_gcd_independently_recomputed" for r in rows)

    signatures: dict[tuple[int, ...], str] = {}
    csv_rows = list(csv.DictReader(CSV.read_text(encoding="utf-8").splitlines()))
    assert len(csv_rows) == len(rows)
    for row, raw in zip(rows, csv_rows):
        summands = tuple(row["summands"])
        e = row["target"]
        check_identity(summands, e)
        assert tuple(sorted(summands)) == summands
        assert all(abs(x) < e for x in summands)
        assert gcd(*summands, e) == 1
        assert sum(x % 5 == 0 for x in (*summands, e)) in (1, 3)
        assert sum(x % 11 == 0 for x in (*summands, e)) in (1, 3)
        assert (all(x > 0 for x in summands)) == (row["domain"] == "strictly_positive")
        assert all(key in registry["source_index"] for key in row["source_ids"])

        # Legacy CSV may use a different ordering of signed terms;
        # the mathematical identity, not source presentation, is canonical.
        old = tuple(int(raw[k]) for k in "abcd")
        old_e = int(raw["e"])
        assert canonical_class(old, old_e) == canonical_class(summands, e)
        assert raw["all_positive"] == str(row["domain"] == "strictly_positive").lower()
        assert int(raw["source_year"]) == row["year"]

        signature = canonical_class(summands, e)
        assert signature not in signatures, "source list repeats equivalent zero-sum identity"
        signatures[signature] = row["id"]

        # Permutations of left terms are the SAME primitive class.
        permuted = (summands[3], summands[0], summands[2], summands[1])
        assert canonical_class(permuted, e) == signature
        # Scaling does not create a new primitive class.
        scaled = tuple(7*x for x in summands)
        assert canonical_class(scaled, 7*e) == signature
        # Moving a positive left term to the target and changing the
        # signs of the remaining terms is the same 5-term identity.
        positive = next(x for x in summands if x > 0)
        others = list(summands)
        others.remove(positive)
        moved = tuple(sorted([e] + [-x for x in others]))
        assert canonical_class(moved, positive) == signature

    assert sum(r["domain"] == "strictly_positive" for r in rows) == 2
    assert sum(r["domain"] == "signed_with_one_negative_summand" for r in rows) == 2
    assert all(sum(x < 0 for x in r["summands"]) == 1 for r in rows if r["domain"] != "strictly_positive")

    # Corruptions must never become declared mathematical discoveries.
    try:
        canonical_class((27, 84, 110, 134), 144)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid fifth-power identity accepted")
    for r in rows:
        assert (r["target"]**5) == sum(x**5 for x in r["summands"])

    print("Audited four literature-reported nontrivial primitive fifth-power identities: "
          "two strictly positive and two signed; exact arithmetic, gcd, "
          "source cross-links and equivalence-class de-duplication passed.")
    return registry


if __name__ == "__main__":
    verify_registry()
