"""Independent Python validation for actual native BigZ record indexing.

The compiler's Mojo implementation is mandatory. Python recomputes each
shard's exact pair sum multimap and all right-pair visits from scratch.
No inference of untested heights or universal compiler correctness.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from math import gcd
import subprocess

from check_research_kernels import ROOT, run_mojo


def test_bigz_probe():
    observed = run_mojo("kernel/bigz_pair_probe.mojo")
    large = 2**63
    expected = [
        "COLLISION 1 4", "COLLISION 2 3",
        "RECORD -7 1 1",
        "RECORD 0 2 2",
        f"RECORD {large} 1 1",
        f"RECORD {large} 1 2",
        f"RECORD {large} 2 2",
        f"RECORD {large + 1} 3 3",
        "HUGEPAIR 1 1", "HUGEPAIR 1 2", "HUGEPAIR 2 2",
        f"BIGGER {large + 1}",
    ]
    assert observed == expected, (observed, expected)
    print("BigZ exact sorted collision and >Int64 probes agree with Python.")


def oracle(start: int, end: int, modulus: int) -> list[str]:
    assert 2 <= start <= end <= 320 and end - start <= 3
    lines = [f"DOMAIN E5BIGSHARDv1 {start} {end} {modulus}"]
    visits_total = 0
    hits_total = 0
    powers = [i**5 for i in range(end + 1)]
    for e in range(start, end + 1):
        exact_pairs: dict[int, list[tuple[int, int]]] = defaultdict(list)
        for a in range(1, e):
            for b in range(a, e):
                exact_pairs[powers[a] + powers[b]].append((a, b))
        visits = Counter()
        hits = Counter()
        for c in range(1, e):
            for d in range(c, e):
                right = powers[c] + powers[d]
                target = powers[e] - right
                if target <= 0:
                    continue
                key = tuple(sorted((target % modulus, right % modulus)))
                visits[key] += 1
                visits_total += 1
                for a, b in exact_pairs.get(target, ()):
                    if b <= c and gcd(a, b, c, d, e) == 1:
                        lines.append(f"CERT E5v1 {a} {b} {c} {d} {e}")
                        hits[key] += 1
                        hits_total += 1
        for lo in range(modulus):
            for hi in range(lo, modulus):
                if (lo + hi) % modulus != powers[e] % modulus:
                    continue
                lines.append(
                    f"PART {e} {lo} {hi} {visits[lo, hi]} {hits[lo, hi]}"
                )
    lines.append(f"SHARD {start} {end} {modulus} {visits_total} {hits_total}")
    return lines


def test_bigz_shards():
    # Disjoint small, historical nonempty witness, radix crossover, and
    # fresh high bounded target heights. No gaps or unknown ranges implied.
    cases = ((2, 5, 7), (143, 144, 35), (255, 257, 35), (319, 320, 35))
    for start, end, m in cases:
        actual = run_mojo("kernel/bigz_shard.mojo", str(start), str(end), str(m))
        expected = oracle(start, end, m)
        assert actual == expected, (
            f"native BigZ shard mismatch at [{start},{end}] mod {m}",
            (Counter(expected) - Counter(actual)).most_common(6),
            (Counter(actual) - Counter(expected)).most_common(6),
        )
        print(f"BigZ shard [{start},{end}], M={m}: {actual[-1]}")

    # Fail-closed resource limits and canonical argument intake.
    for args in (
        ("1", "2", "35"), ("2", "321", "35"), ("2", "6", "35"),
        ("10", "9", "35"), ("2", "3", "0"), ("2", "3", "1"),
        ("2", "3", "36"), ("02", "3", "35"),
    ):
        result = subprocess.run(
            ["bash", "scripts/run_mojo.sh", "kernel/bigz_shard.mojo", *args],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert result.returncode != 0, (args, result.stdout)
    print("BigZ bound and malformed-argument rejections verified.")


if __name__ == "__main__":
    test_bigz_probe()
    test_bigz_shards()
