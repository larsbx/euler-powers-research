"""Independent exact-Python oracle of bounded E5 digit/CRT rejections.

Mojo actually runs the shared pinned PairPowerResiduePrefix implementation.
This oracle uses Python sets, recomputes fifth powers independently, and
never substitutes its own stream for native output. Not a speedup claim.
"""
from __future__ import annotations

from check_research_kernels import run_mojo


def oracle(bound: int, modulus: int) -> tuple[int, int]:
    assert 2 <= bound <= 144
    prefix: set[int] = set()
    powers = [x ** 5 for x in range(bound + 1)]
    count = rejected = 0
    for c in range(1, bound):
        prefix.update((powers[a] + powers[c]) % modulus for a in range(1, c + 1))
        for e in range(c + 1, bound + 1):
            for d in range(c, e):
                complement = powers[e] - powers[c] - powers[d]
                if complement <= 0:
                    continue
                count += 1
                if complement % modulus not in prefix:
                    rejected += 1
    return count, rejected


def main() -> None:
    native = run_mojo("kernel/digit_filter_probe.mojo")
    expected = []
    for bound in (8, 48, 144):
        for modulus in (9, 11, 25, 99, 2475):
            visits, rejected = oracle(bound, modulus)
            expected.append(f"SIEVE {bound} {modulus} {visits} {rejected} {visits-rejected}")
    expected.append("WITNESS 1881")
    assert native == expected, (native, expected)
    reference = {
        9: 21873, 11: 152879, 25: 133804, 99: 181825, 2475: 356770
    }
    for modulus, rejected in reference.items():
        assert oracle(144, modulus) == (475063, rejected)
    # A genuine primitive solution cannot be filtered. A modular
    # pass is only a *necessary* condition, not evidence of a witness.
    known = (27, 84, 110, 133, 144)
    a, b, c, d, e = known
    assert a**5 + b**5 + c**5 + d**5 == e**5
    assert (a**5 + b**5) % 2475 == 1881
    assert (e**5 - c**5 - d**5) % 2475 == 1881
    print("Native digit/CRT prefilter and 75.1% bounded rejection agree with Python.")


if __name__ == "__main__":
    main()
