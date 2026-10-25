"""Independent Python exact-integer comparison of native shared-kernel adapter.

The Mojo executable is mandatory; compilation failures never fall back to
Python. Any mismatch, overflow acceptance or missing case fails CI.
"""
from __future__ import annotations

from math import gcd

from check_research_kernels import run_mojo


def main() -> None:
    native = run_mojo("kernel/euler_exact_probe.mojo")
    expected: list[str] = []
    for x in (-6208, -1000, -144, -2, -1, 0, 1, 2, 144, 1000, 6208):
        expected.append(f"FIFTH {x} {x**5}")
    for x in (-1_000_000_000, -6209, 6209, 1_000_000_000):
        assert not -(2**63) <= x**5 < 2**63
        expected.append(f"BIGZ {x} {x**5}")
    expected.extend(
        [
            "SUM 579",
            "COMPLEMENT 50",
            f"PACK {(5 * 145 + 1) * 145 + 4}",
            f"PACK {(5 * 145 + 2) * 145 + 3}",
            "PRIMITIVE ACCEPT",
            "NONPRIMITIVE REJECT",
            "REFUSED FIFTH -6209",
            "REFUSED FIFTH 6209",
            "REFUSED PAIR",
            "REFUSED COMPLEMENT",
            "REFUSED PACK",
            "REFUSED DIGIT",
        ]
    )
    assert gcd(27, 84, 110, 133, 144) == 1
    assert gcd(54, 168, 220, 266, 288) == 2
    assert native == expected, (
        "native exact-arithmetic boundary mismatch",
        [x for x, y in zip(native, expected) if x != y][:5],
        len(native),
        len(expected),
    )
    print(
        f"Shared-kernel exact arithmetic: {len(expected)} probes passed "
        "(signed powers, BigZ, packed collisions and overflow refusal)."
    )


if __name__ == "__main__":
    main()
