"""Exact independent oracle for shared prime-power ring profiles and CRT images.

The primary native Mojo results come from the pinned Modulus implementation.
This reference enumerates Python residues and a set-valued DP, not native
Mojo booleans, and never treats finite feasibility as an integer theorem.
"""
from __future__ import annotations

from math import gcd

from check_research_kernels import run_mojo


CASES = ((5, 5), (25, 5), (125, 5), (625, 5),
         (11, 11), (121, 11), (31, 31), (61, 61))
COPRIME = ((25, 11), (125, 11), (25, 31))


def reference(modulus: int, prime: int) -> tuple[int, int, int]:
    fifth_residues = {pow(x, 5, modulus) for x in range(modulus)}
    choices = {
        (pow(x, 5, modulus), int(x % prime == 0))
        for x in range(modulus)
    }
    # Algebraically identical residues can arise from several bases;
    # retain all zero-flag alternatives if they occur.
    states = {(0, 0)}
    for slot in range(5):
        states = {
            ((r + (-power if slot == 4 else power)) % modulus, z + flag)
            for r, z in states
            for power, flag in choices
        }
    mask = sum(1 << z for z in range(6) if (0, z) in states)
    return len(fifth_residues), len(choices), mask


def crt_reference(a: int, b: int) -> int:
    assert gcd(a, b) == 1
    image_a = {pow(x, 5, a) for x in range(a)}
    image_b = {pow(x, 5, b) for x in range(b)}
    # Explicitly verify the residue-pair map is bijective, not a
    # statistical independence assumption.
    projection = {(x % a, x % b) for x in range(a * b)}
    assert projection == {(x, y) for x in range(a) for y in range(b)}
    actual = {pow(x, 5, a * b) for x in range(a * b)}
    assert {(z % a, z % b) for z in actual} == {
        (x, y) for x in image_a for y in image_b
    }
    return len(actual)


def test_run() -> None:
    actual = run_mojo("kernel/prime_power_sieve.mojo")
    expected: list[str] = []
    for m, p in CASES:
        assert m <= 625 and p > 1 and m % p == 0
        k = m
        while k % p == 0:
            k //= p
        assert k == 1
        distinct, choices, mask = reference(m, p)
        expected.append(f"POWER {m} {p} {distinct} {choices} {mask}")
    for a, b in COPRIME:
        actual_image = crt_reference(a, b)
        predicted = reference(a, a if a in (11, 31, 61) else 5)[0] * (
            reference(b, b if b in (11, 31, 61) else 5)[0]
        )
        assert actual_image == predicted
        expected.append(f"CRT {a} {b} {a*b} {actual_image}")
    assert actual == expected, (actual, expected)
    assert reference(25, 5)[2] == 42
    assert reference(125, 5)[2] == 42
    assert reference(121, 11)[2] == 42
    assert reference(31, 31)[2] == 47
    print("Prime-power and CRT native ring profiles agree with independent exact Python oracle.")


if __name__ == "__main__":
    test_run()
