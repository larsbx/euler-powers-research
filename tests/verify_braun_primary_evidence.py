"""Offline, exact-arithmetic audit of the Braun arXiv v4 evidence record.

This test verifies the recorded tuple, sign domain, primitive gcd, exact
fifth-power equality, and the paper's *reported* coverage metadata against
frozen, independently transcribed primary-source values. It does NOT
independently verify any multi-million-height exhaustive-search claim.
"""

from __future__ import annotations

import copy
import csv
import json
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data/literature/braun_2603_05549_v4.json"
SOLUTIONS = ROOT / "data/known_solutions.csv"

EXPECTED_TUPLE = (719115, 1331622, -1340632, 1956213, 1956878)
EXPECTED_COVERAGE = (
    ("nonnegative_integers", 2760000, 2760000, 4000000),
    ("signed_integers", 1450000, 1450000, 2000000),
)


def verify_evidence(record: dict, solution_rows: list[dict[str, str]]) -> None:
    assert record["schema"] == "euler-power-primary-source-audit-v1"
    source = record["source"]
    assert source["id"] == "arxiv:2603.05549v4"
    assert source["author"] == "Jeffrey M. Braun"
    assert source["submitted"] == "2026-03-05"
    assert source["last_revised"] == "2026-08-21"
    assert source["primary_url"] == "https://arxiv.org/html/2603.05549v4"
    assert source["publication_status"] == "arxiv_preprint"

    entry = record["exact_reported_identity"]
    tup = tuple(entry[key] for key in ("a", "b", "c", "d", "e"))
    assert tup == EXPECTED_TUPLE, "source tuple disagrees with Braun v4"
    assert all(type(x) is int for x in tup)
    assert entry["domain"] == "signed_integers"
    assert entry["positive_only"] is False
    assert entry["primitive"] is True
    assert tup[2] < 0 and all(x > 0 for i, x in enumerate(tup) if i != 2)
    assert sum(x**5 for x in tup[:4]) == tup[-1] ** 5
    assert gcd(*tup) == 1
    for p in (5, 11):
        assert sum(x % p == 0 for x in tup) in (1, 3)

    coverage = record["author_reported_search_coverage"]
    got = tuple(
        (
            line["domain"],
            line["exhaustive_e_le"],
            line["partial_e_gt"],
            line["partial_e_le"],
        )
        for line in coverage
    )
    assert got == EXPECTED_COVERAGE, (
        "paper distinguishes 2.76M/4M nonnegative and "
        "1.45M/2M signed search coverage"
    )
    for domain, full, partial_after, partial_end in got:
        assert all(type(v) is int for v in (full, partial_after, partial_end))
        assert 0 < full == partial_after < partial_end

    effort = record["author_reported_resources"]
    assert effort["iterations_approximately"] == "5.4e18"
    assert effort["vcpu_hours_approximately"] == 10500000
    assert effort["execution_period"] == "approximately nine months"
    assert record["author_reported_implementation"]["integer_arithmetic"] == "signed __int128"
    assert record["author_reported_implementation"]["language"] == "C++"
    evidence = record["evidence"]
    assert evidence["identity_and_gcd"] == "independently_checked_by_repo_python_and_mojo"
    assert evidence["coverage_and_resource_claims"] == (
        "author_report_only_not_independently_reproduced"
    )
    assert evidence["positive_count_classification"] == (
        "two_positive_of_four_reported_primitive_identities"
    )
    assert sorted(evidence["not_a_proof_of"]) == [
        "E5-1", "E5-2", "E5-3", "E5-4", "E5-5"
    ]

    assert len(solution_rows) == 4
    labeled_braun = [row for row in solution_rows if row["source"] == "Braun"]
    assert len(labeled_braun) == 1
    assert labeled_braun[0]["source_year"] == "2026"
    assert labeled_braun[0]["all_positive"] == "false"
    assert tuple(int(labeled_braun[0][key]) for key in "abcde") == tup
    assert sum(row["all_positive"] == "true" for row in solution_rows) == 2
    for row in solution_rows:
        values = tuple(int(row[key]) for key in "abcde")
        assert gcd(*values) == 1
        assert sum(v**5 for v in values[:4]) == values[4] ** 5
        assert (all(v > 0 for v in values)) == (row["all_positive"] == "true")


def regression_rejections(record: dict, rows: list[dict[str, str]]) -> None:
    """Fail if a changed record would silently upgrade or misclassify evidence."""
    variants = []

    changed = copy.deepcopy(record)
    changed["exact_reported_identity"]["c"] = -1340631
    variants.append(changed)

    changed = copy.deepcopy(record)
    changed["exact_reported_identity"]["positive_only"] = True
    variants.append(changed)

    changed = copy.deepcopy(record)
    changed["author_reported_search_coverage"][0]["exhaustive_e_le"] = 4000000
    variants.append(changed)

    changed = copy.deepcopy(record)
    changed["author_reported_search_coverage"][1]["domain"] = "nonnegative_integers"
    variants.append(changed)

    changed = copy.deepcopy(record)
    changed["evidence"]["coverage_and_resource_claims"] = "independently_reproduced"
    variants.append(changed)

    changed = copy.deepcopy(record)
    changed["source"]["id"] = "arxiv:2603.05549v3"
    variants.append(changed)

    for variant in variants:
        try:
            verify_evidence(variant, rows)
        except AssertionError:
            continue
        raise AssertionError("corrupted literature evidence was accepted")


def main() -> None:
    record = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    with SOLUTIONS.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    verify_evidence(record, rows)
    regression_rejections(record, rows)
    print(
        "Braun arXiv 2603.05549v4: exact signed primitive identity verified; "
        "2 positive of 4 recorded tuples; 6 metadata corruptions rejected. "
        "Search coverage remains an externally reported claim, not reproduced."
    )


if __name__ == "__main__":
    main()
