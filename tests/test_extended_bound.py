"""Strict independent B145/B256 extension acceptance, not an unbounded search.

Replays actual native Mojo stdout, compares all rows/certs to an
independently enumerated exact Python hash-multimap oracle and pins a
new B256/M35 per-key SHA-256 replay root.
"""
from __future__ import annotations

from collections import Counter

from check_research_kernels import run_mojo
from replay_partition import replay
from test_pair_partition import oracle, expected_stream

ROOT256 = "157fdbc83048ddc782d8aa04c9691d0c34dabfaf96819a6976dd6671e284e07e"
WITNESS = (27, 84, 110, 133, 144)


def main():
    for bound in (145, 256):
        lines = run_mojo("kernel/pair_partition.mojo", str(bound), "35")
        assert Counter(lines) == expected_stream(bound, 35), f"B={bound}: full independent stream mismatch"
        expected_parts, expected_certs = oracle(bound, 35)
        report = replay(
            lines, bound, 35, expected_parts, expected_certs,
            ROOT256 if bound == 256 else None,
        )
        assert expected_certs == [WITNESS], (bound, expected_certs)
        assert report["certificates"] == 1
        assert report["partition_rows"] == len(expected_parts)
        if bound == 256:
            assert report["partition_rows"] == 4590
            assert report["right_pair_visits"] == 2664481
            assert report["root_sha256"] == ROOT256
        print(f"B={bound}, M=35: {report['partition_rows']} exact PART rows, "
              f"{report['right_pair_visits']} visits, one primitive positive witness.")
    print("B145/B256 independent exact Mojo/Python and replay checks passed.")


if __name__ == "__main__":
    main()
