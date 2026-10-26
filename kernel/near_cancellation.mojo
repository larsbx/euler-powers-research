"""Discovery-oriented exact near-cancellation search for positive primitive E5.

Search one (e, delta=e-d) slice without relying on a known witness.
For 1<=a<=A and a<=b<=c<=d<e, solve

    b^5 = e^5 - (e-delta)^5 - c^5 - a^5.

A complete bounded c interval follows from c^5<=D<=3*c^5,
where D=e^5-d^5. Canonical modular fifth-power prefilter is ONLY a
necessary condition; final membership uses exact shared BigZ powers.
This does not cover a>A, any other delta, or any other e.
"""
from std.sys import argv
from certified_records.codec import parse_canonical
from finite_exact.bigint_z import (
    BigZ, bigz_from_i64, bigz_mul, bigz_sub, bigz_lt, bigz_eq
)
from finite_polynomial.polynomial_fp import Modulus
from euler_exact import fifth_bigz, primitive5


def max_fifth_root(value: BigZ, upper: Int) -> Int:
    """Largest nonnegative x<=upper with x^5<=value."""
    var lo = 0
    var hi = upper + 1
    while lo + 1 < hi:
        var mid = lo + (hi - lo) // 2
        if not bigz_lt(value, fifth_bigz(Int64(mid))):
            lo = mid
        else:
            hi = mid
    return lo


def min_three_fifth_root(
    value: BigZ, upper: Int
) -> Int:
    """Smallest nonnegative x<=upper with 3*x^5>=value, or upper+1."""
    var lo = 0
    var hi = upper + 1
    var triple = bigz_from_i64(3)
    while lo < hi:
        var mid = lo + (hi - lo) // 2
        var trial = bigz_mul(triple, fifth_bigz(Int64(mid)))
        if bigz_lt(trial, value):
            lo = mid + 1
        else:
            hi = mid
    return lo


def b_fifth_lower_bound(
    powers: List[BigZ], target: BigZ, lo: Int, hi_inclusive: Int
) -> Int:
    """First b in [lo, hi+1] whose exact b^5>=target."""
    var low = lo
    var hi = hi_inclusive + 1
    while low < hi:
        var mid = low + (hi - low) // 2
        if bigz_lt(powers[mid], target):
            low = mid + 1
        else:
            hi = mid
    return low


def search(e: Int, delta: Int, max_a: Int) raises:
    if (e < 5 or e > 100000 or delta < 1 or delta >= e or
        delta > 256 or max_a < 1 or max_a > 128):
        raise Error("require 5<=e<=100000, 1<=delta<=256<e, 1<=A<=128")

    var d = e - delta
    var remaining = bigz_sub(
        fifth_bigz(Int64(e)), fifth_bigz(Int64(d))
    )
    # Every ordered positive solution has c<=d and
    # a^5+b^5+c^5=D; therefore D<=3*c^5 and c^5<=D.
    var c_upper = max_fifth_root(remaining, d)
    var c_lower = min_three_fifth_root(remaining, d)
    var width = max(0, c_upper - c_lower + 1)
    if width > 10000 or width * max_a > 1280000:
        raise Error("slice exceeds reviewed finite work budget")

    print("DOMAIN E5DELTA-v1", e, delta, max_a)
    print("BOUNDS", c_lower, c_upper, d)
    if width == 0:
        print("SUMMARY", 0, 0, 0, 0, 0)
        return

    var powers = List[BigZ]()
    var ring = Modulus(99000)
    var residue_seen = List[Bool](length=99000, fill=False)
    for x in range(c_upper + 1):
        powers.append(fifth_bigz(Int64(x)))

    var trials = 0
    var rejected = 0
    var lookups = 0
    var hits = 0
    # Build the complete mod-99000 b^5 prefix, including each b<=c.
    # No probabilistic independence or prime-field assumption.
    for b in range(1, c_lower):
        residue_seen[ring.pow(b, 5)] = True
    for c in range(c_lower, c_upper + 1):
        residue_seen[ring.pow(c, 5)] = True
        var left = bigz_sub(remaining, powers[c])
        for a in range(1, min(max_a, c) + 1):
            trials += 1
            var target = bigz_sub(left, powers[a])
            if target.sign <= 0:
                rejected += 1
                continue
            if not residue_seen[ring.reduce_bigz(target)]:
                rejected += 1
                continue
            lookups += 1
            var b = b_fifth_lower_bound(powers, target, a, c)
            if b <= c and bigz_eq(powers[b], target):
                if primitive5(Int64(a), Int64(b), Int64(c),
                              Int64(d), Int64(e)):
                    print("CERT E5v1", a, b, c, d, e)
                    hits += 1
    print("SUMMARY", width, trials, rejected, lookups, hits)


def main() raises:
    var args = List[String]()
    for arg in argv():
        args.append(String(arg))
    if len(args) != 4:
        raise Error("usage: near_cancellation E DELTA A_MAX")
    var e = parse_canonical(args[1], 32)
    var delta = parse_canonical(args[2], 32)
    var max_a = parse_canonical(args[3], 32)
    if not e or not delta or not max_a:
        raise Error("noncanonical discovery slice input")
    search(Int(e.value()), Int(delta.value()), Int(max_a.value()))
