"""Independent Python oracle for Mojo finite-ring DP and bounded positive E5 census.

No Python result is trusted by the Mojo kernel: they compute from the same
definition through different data structures. All arithmetic is exact.
"""
from __future__ import annotations

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from math import gcd
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
MODULI = ((7, 7), (11, 11), (25, 5), (31, 31))


def run_mojo(*args: str) -> list[str]:
    completed = subprocess.run(
        ["bash", "scripts/run_mojo.sh", *args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.splitlines()


def ring_reference(modulus: int, prime: int) -> tuple[int, int, int]:
    residue_values = {pow(x, 5, modulus) for x in range(modulus)}
    states: set[tuple[int, int]] = {(0, 0)}
    for slot in range(5):
        choices = tuple(
            ((-1 if slot == 4 else 1) * pow(x, 5, modulus), int(x % prime == 0))
            for x in range(modulus)
        )
        states = {
            ((residue + signed_power) % modulus, zeros + is_zero)
            for residue, zeros in states
            for signed_power, is_zero in choices
        }
    mask = sum(1 << z for z in range(6) if (0, z) in states)
    return modulus, len(residue_values), mask


def check_ring() -> None:
    actual = run_mojo("kernel/residue_sieve.mojo")
    expected = [
        f"MOD {m} {cardinality} {mask}"
        for m, p in MODULI
        for _, cardinality, mask in (ring_reference(m, p),)
    ]
    assert actual == expected, (actual, expected)
    assert ring_reference(11, 11)[2] == 42
    assert ring_reference(25, 5)[2] == 42
    print("Exact Mojo finite-ring DP agrees with independent Python oracle.")


def python_census(max_e: int, start_e: int = 2) -> list[tuple[int, int, int, int, int]]:
    powers = [x**5 for x in range(max_e + 1)]
    found: list[tuple[int, int, int, int, int]] = []
    for e in range(start_e, max_e + 1):
        # Hash-indexed pairing is algorithmically distinct from the Mojo
        # sorted-array / binary-search construction.
        pairs: dict[int, list[tuple[int, int]]] = defaultdict(list)
        for a in range(1, e):
            for b in range(a, e):
                pairs[powers[a] + powers[b]].append((a, b))
        for c in range(1, e):
            for d in range(c, e):
                for a, b in pairs.get(powers[e] - powers[c] - powers[d], ()):
                    if b <= c and gcd(a, b, c, d, e) == 1:
                        found.append((a, b, c, d, e))
    return found


def parse_census(lines: list[str], max_e: int, start_e: int | None = None) -> list[tuple[int, int, int, int, int]]:
    assert lines, "Mojo did not print census"
    last = lines[-1].split()
    assert last[:1] == ["CENSUS"], lines
    if start_e is None:
        assert len(last) == 3 and last[1] == str(max_e), lines
    else:
        assert len(last) == 4 and last[1:3] == [str(start_e), str(max_e)], lines
    assert last[-1].isascii() and last[-1].isdecimal()
    found: list[tuple[int, int, int, int, int]] = []
    for line in lines[:-1]:
        parts = line.split(" ")
        assert len(parts) == 7 and parts[0:2] == ["CERT", "E5v1"], line
        assert all(p.isascii() and p.isdecimal() and str(int(p)) == p for p in parts[2:])
        a, b, c, d, e = map(int, parts[2:])
        assert 0 < a <= b <= c <= d < e <= max_e
        if start_e is not None:
            assert e >= start_e
        assert a**5 + b**5 + c**5 + d**5 == e**5
        assert gcd(a, b, c, d, e) == 1
        found.append((a, b, c, d, e))
    assert len(found) == int(last[-1]) and len(set(found)) == len(found)
    return found


def certificate_digest(found: list[tuple[int, int, int, int, int]]) -> str:
    # Canonical sorted records with domain separation; independent of the
    # traversal order, platform, locale, or Mojo hash-table internals.
    records = "".join(
        "CERT E5v1 " + " ".join(map(str, tup)) + "\n"
        for tup in sorted(found, key=lambda t: (t[4], t[0], t[1], t[2], t[3]))
    )
    return sha256(("E5-CERTIFICATES-v1\n" + records).encode("ascii")).hexdigest()


def check_census(max_e: int) -> None:
    lines = run_mojo("kernel/positive_census.mojo", str(max_e))
    got = parse_census(lines, max_e)
    expected = python_census(max_e)
    assert sorted(got) == sorted(expected), (got, expected)
    if max_e == 144:
        assert got == [(27, 84, 110, 133, 144)]
        fixture = (ROOT / "certificates/census_e144.txt").read_text(encoding="utf-8").splitlines()
        assert lines == fixture, "published certificate fixture differs from census"
    print(
        f"Complete positive primitive census e<= {max_e}: {len(got)} solution(s); "
        f"certificate_sha256={certificate_digest(got)}"
    )


def check_shards() -> None:
    # Two workers execute independent Mojo processes, each owning an exact,
    # nonoverlapping closed height interval. The merge checks the full corpus.
    ranges = ((2, 72), (73, 144))
    assert ranges[0][0] == 2 and ranges[-1][1] == 144
    assert all(a < b for (_, a), (b, _) in zip(ranges, ranges[1:]))
    assert ranges[0][1] + 1 == ranges[1][0]
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(run_mojo, "kernel/positive_census.mojo", str(lo), str(hi))
            for lo, hi in ranges
        ]
        results = [future.result() for future in futures]
    combined: list[tuple[int, int, int, int, int]] = []
    for (lo, hi), lines in zip(ranges, results):
        got = parse_census(lines, hi, start_e=lo)
        assert sorted(got) == sorted(python_census(hi, start_e=lo))
        combined.extend(got)
    full = python_census(144)
    assert len(combined) == len(set(combined))
    assert sorted(combined) == sorted(full)
    print("Two disjoint Mojo shards cover e<=144 with no gaps or duplicate certificates.")


def check_negative_cases() -> None:
    for bad in (
        [],
        ["CERT E5v1 27 84 110 133 145", "CENSUS 144 1"],
        ["CERT E5v1 27 84 110 133 144", "CENSUS 144 0"],
        ["CERT E5v1 027 84 110 133 144", "CENSUS 144 1"],
        ["CERT E5v1 54 168 220 266 288", "CENSUS 288 1"],
    ):
        try:
            parse_census(bad, 144)
        except AssertionError:
            pass
        else:
            raise AssertionError(f"malformed or nonprimitive certificate accepted: {bad}")


def check_input_guards() -> None:
    # Every rejected case must fail explicitly at the Mojo entry point.
    bad_args = [
        ("0",), ("1",), ("1001",), ("-1",), ("02",),
        ("2", "1001"), ("80", "79"), ("0", "20"),
        ("-1", "20"), ("20", "00020"),
    ]
    for args in bad_args:
        command = ["bash", "scripts/run_mojo.sh", "kernel/positive_census.mojo", *args]
        result = subprocess.run(
            command, cwd=ROOT, text=True, capture_output=True,
            check=False, timeout=90,
        )
        assert result.returncode != 0, (args, result.stdout, result.stderr)
    result = run_mojo("kernel/positive_census.mojo", "2")
    assert result == ["CENSUS 2 0"], result
    print("Mojo bounded Int64 intake: 10 invalid requests refused; height 2 accepted.")


def main() -> None:
    check_ring()
    check_input_guards()
    check_negative_cases()
    check_census(16)
    check_census(144)
    check_shards()


if __name__ == "__main__":
    main()
