"""Independent exact Python oracle for discovery-oriented Mojo delta slices.

A Python dictionary indexed by b^5 is intentionally a different
algorithm from Mojo's sorted fifth-power binary search. The oracle
does NOT rely on the residue prefilter when deciding witnesses:
it separately validates exact arithmetic, primitivity and ordering.
"""
from __future__ import annotations

from math import gcd
import subprocess

from check_research_kernels import ROOT, run_mojo


def fifth_floor(n: int, upper: int) -> int:
    lo, hi = 0, upper + 1
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid**5 <= n:
            lo = mid
        else:
            hi = mid
    return lo


def fifth_three_ceil(n: int, upper: int) -> int:
    lo, hi = 0, upper + 1
    while lo < hi:
        mid = (lo + hi) // 2
        if 3 * mid**5 < n:
            lo = mid + 1
        else:
            hi = mid
    return lo


def oracle(e: int, delta: int, max_a: int) -> list[str]:
    assert 5 <= e <= 100000 and 1 <= delta <= 256 and delta < e
    assert 1 <= max_a <= 128
    d = e - delta
    difference = e**5 - d**5
    lower = fifth_three_ceil(difference, d)
    upper = fifth_floor(difference, d)
    width = max(0, upper - lower + 1)
    assert width <= 10000 and width * max_a <= 1280000

    lines = [
        f"DOMAIN E5DELTA-v1 {e} {delta} {max_a}",
        f"BOUNDS {lower} {upper} {d}"
    ]
    if width == 0:
        return lines + ["SUMMARY 0 0 0 0 0"]
    powers = [i**5 for i in range(upper + 1)]
    fifth_to_base = {value: b for b, value in enumerate(powers)}
    # Python's separately enumerated fifth-residue membership acts as
    # a measurement oracle, never as the witness existence test.
    available = set(pow(i, 5, 99000) for i in range(1, lower))
    trials = rejected = lookups = 0
    witnesses = []
    for c in range(lower, upper + 1):
        available.add(powers[c] % 99000)
        for a in range(1, min(max_a, c) + 1):
            trials += 1
            target = difference - powers[c] - powers[a]
            if target <= 0 or target % 99000 not in available:
                rejected += 1
                continue
            lookups += 1
            b = fifth_to_base.get(target)
            if b is not None and a <= b <= c and gcd(a, b, c, d, e) == 1:
                assert powers[a] + powers[b] + powers[c] + d**5 == e**5
                witnesses.append((a, b, c, d, e))
                lines.append("CERT E5v1 " + " ".join(map(str, witnesses[-1])))
    lines.append(f"SUMMARY {width} {trials} {rejected} {lookups} {len(witnesses)}")
    return lines


def main():
    old = (27, 84, 110, 133, 144)
    frye = (55, 3183, 28969, 85282, 85359)
    known = (old, frye)
    for a, b, c, d, e in known:
        assert sum(x**5 for x in (a, b, c, d)) == e**5
        assert gcd(a, b, c, d, e) == 1
    cases = ((144, 11, 64), (85359, 77, 64), (85360, 77, 64))
    for e, delta, small_a in cases:
        observed = run_mojo("kernel/near_cancellation.mojo",
                            str(e), str(delta), str(small_a))
        expected = oracle(e, delta, small_a)
        assert observed == expected, (
            "native near-cancellation diverges from independent exact Python",
            e, delta, small_a,
            observed[:8], expected[:8], observed[-1:], expected[-1:]
        )
        certs = [row for row in expected if row.startswith("CERT ")]
        if e == 144:
            assert certs == ["CERT E5v1 " + " ".join(map(str, old))]
        if e == 85359:
            assert certs == ["CERT E5v1 " + " ".join(map(str, frye))]
        if e == 85360:
            # Negative result applies ONLY to this exact (e,delta,a-cap).
            assert certs == []
        print(f"DISCOVERY SLICE e={e} delta={delta} a<=64: "
              f"{expected[1]}; {expected[-1]}; {len(certs)} known/new.")

    for args in (("144", "0", "64"), ("85359", "77", "0"),
                 ("100001", "77", "64"), ("85359", "257", "64"),
                 ("85359", "77", "129"), ("085359", "77", "64")):
        process = subprocess.run(
            ["bash", "scripts/run_mojo.sh", "kernel/near_cancellation.mojo", *args],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert process.returncode != 0, (args, process.stdout)
    print("Discovery regression calibrated on both previously known "
          "primitive positive solutions; one forward finite slice verified.")


if __name__ == "__main__":
    main()
