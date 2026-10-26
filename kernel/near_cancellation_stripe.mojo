"""Novelty-territory exact E5 near-cancellation stripe (Mojo, BigZ).

For fixed e, delta=e-d and A_MIN<=abs(a)<=A, search ALL admissible ordered pairs
(a,c) in a declared contiguous c interval. The full c interval follows
from D=e^5-d^5 <= 3c^5 and c^5 <= D+A^5 for a negative
first summand (c^5 <= D for positive a). Require abs(a)<=b<=c<=d.  A stripe is never a height-complete census.

The only modular rejection is the complete fifth-power image of b<=c;
final witnesses require exact fifth powers and five-way primitive gcd.
No floating point, heuristic rounding or packed sum used.
"""
from std.sys import argv
from certified_records.codec import parse_canonical
from finite_exact.bigint_z import (
    BigZ, bigz_from_i64, bigz_add, bigz_mul, bigz_sub, bigz_lt, bigz_eq
)
from finite_polynomial.polynomial_fp import Modulus
from euler_exact import fifth_bigz, primitive5
from near_cancellation import (
    max_fifth_root, min_three_fifth_root, b_fifth_lower_bound
)


def min_two_fifth_root(value: BigZ, upper: Int) -> Int:
    """Least nonnegative x with 2*x^5>=value, or upper+1."""
    var lo = 0
    var hi = upper + 1
    var two = bigz_from_i64(2)
    while lo < hi:
        var mid = lo + (hi-lo)//2
        if bigz_lt(bigz_mul(two, fifth_bigz(Int64(mid))), value):
            lo = mid + 1
        else:
            hi = mid
    return lo


def search_stripe(
    e: Int, delta: Int, max_a: Int, c_start: Int, c_end: Int,
    min_a: Int = 1, negative: Bool = False, tight: Bool = False
) raises:
    # Resource policy, not a mathematical upper bound on E5.
    if (e < 5 or e > 4000000 or delta < 1 or delta > 256 or
        delta >= e or min_a < 1 or min_a > max_a or max_a > 1024 or
        c_start < 1 or c_start > c_end or c_end >= e or
        c_end - c_start >= 4096 or c_end > 600000):
        raise Error("E5STRIPE range or explicit resource budget exceeded")
    var d = e - delta
    var remainder = bigz_sub(
        fifth_bigz(Int64(e)), fifth_bigz(Int64(d))
    )
    var c_min = min_three_fifth_root(remainder, d)
    if tight:
        var threshold = remainder.copy()
        if not negative:
            threshold = bigz_sub(remainder, fifth_bigz(Int64(max_a)))
        c_min = max(c_min, min_two_fifth_root(threshold,d))
    var upper_remainder = remainder.copy()
    if negative:
        upper_remainder = bigz_add(remainder, fifth_bigz(Int64(max_a)))
    var c_max = max_fifth_root(upper_remainder, d)
    if c_start < c_min or c_end > c_max:
        raise Error("stripe exceeds mathematically admissible c bounds")

    if tight:
        print("DOMAIN E5STRIPEv3", e, delta, min_a, max_a,
              Int(negative), c_start, c_end)
    elif min_a == 1 and not negative:
        print("DOMAIN E5STRIPEv1", e, delta, max_a, c_start, c_end)
    else:
        print("DOMAIN E5STRIPEv2", e, delta, min_a, max_a,
              Int(negative), c_start, c_end)
    print("BOUNDS", c_min, c_max, d)

    # Cache *exact* fifth powers up to the right edge. Memory O(c_end).
    # The complete modular b-image is built independently from every
    # 1<=b<=c, not an assumed prime-field/CRT distribution.
    var powers = List[BigZ]()
    for b in range(c_end + 1):
        powers.append(fifth_bigz(Int64(b)))
    var ring = Modulus(99000)
    # Extra exact fifth-power images modulo primes with 5 | (p-1).
    # These are necessary conditions for the SAME admissible b<=c,
    # not probabilistic CRT guesses or field lifting assumptions.
    var ring41 = Modulus(41)
    var ring61 = Modulus(61)
    var fifth_seen = List[Bool](length=99000, fill=False)
    var seen41 = List[Bool](length=41, fill=False)
    var seen61 = List[Bool](length=61, fill=False)
    for b in range(1, c_start):
        fifth_seen[ring.pow(b, 5)] = True
        seen41[ring41.pow(b, 5)] = True
        seen61[ring61.pow(b, 5)] = True

    var trials = 0
    var rejected = 0
    var lookups = 0
    var witnesses = 0
    for c in range(c_start, c_end + 1):
        fifth_seen[ring.pow(c, 5)] = True
        seen41[ring41.pow(c, 5)] = True
        seen61[ring61.pow(c, 5)] = True
        var left = bigz_sub(remainder, powers[c])
        for a in range(min_a, min(c, max_a) + 1):
            trials += 1
            var signed_a = a
            if negative:
                signed_a = -a
            var candidate = bigz_sub(left, powers[a])
            if negative:
                candidate = bigz_add(left, powers[a])
            if candidate.sign <= 0:
                rejected += 1
                continue
            if not fifth_seen[ring.reduce_bigz(candidate)]:
                rejected += 1
                continue
            if not seen41[ring41.reduce_bigz(candidate)]:
                rejected += 1
                continue
            if not seen61[ring61.reduce_bigz(candidate)]:
                rejected += 1
                continue
            lookups += 1
            var b = b_fifth_lower_bound(powers, candidate, a, c)
            if b <= c and bigz_eq(powers[b], candidate):
                if primitive5(Int64(a), Int64(b), Int64(c),
                              Int64(d), Int64(e)):
                    # The one signed term and remaining positive terms are ordered by magnitude.
                    # Recheck exact identity at the admission boundary.
                    var lhs = fifth_bigz(Int64(e))
                    var computed = bigz_sub(lhs, powers[c])
                    computed = bigz_sub(computed, fifth_bigz(Int64(signed_a)))
                    computed = bigz_sub(computed, powers[b])
                    if not bigz_eq(computed, fifth_bigz(Int64(d))):
                        raise Error("BigZ stripe candidate failed exact identity")
                    print("CERT E5v1", signed_a, b, c, d, e)
                    witnesses += 1
    print("SUMMARY", c_end - c_start + 1,
          trials, rejected, lookups, witnesses)


def main() raises:
    var args = List[String]()
    for arg in argv():
        args.append(String(arg))
    if len(args) != 6 and len(args) != 8 and len(args) != 9:
        raise Error("usage: near_cancellation_stripe E DELTA A C_LO C_HI [A_MIN NEGATIVE_0_OR_1 [TIGHT_0_OR_1]]")
    var e = parse_canonical(args[1], 32)
    var delta = parse_canonical(args[2], 32)
    var a = parse_canonical(args[3], 32)
    var lower = parse_canonical(args[4], 32)
    var upper = parse_canonical(args[5], 32)
    if not e or not delta or not a or not lower or not upper:
        raise Error("noncanonical integer search stripe")
    var min_a = 1
    var negative = False
    if len(args) >= 8:
        var lower_a = parse_canonical(args[6], 32)
        var neg = parse_canonical(args[7], 32)
        if not lower_a or not neg:
            raise Error("noncanonical summand interval/sign")
        if neg.value() > 1:
            raise Error("negative flag must be 0 or 1")
        min_a = Int(lower_a.value())
        negative = neg.value() == 1
    var tight = False
    if len(args) == 9:
        var flag = parse_canonical(args[8], 32)
        if not flag:
            raise Error("noncanonical tight bound flag")
        if flag.value() > 1:
            raise Error("tight bound flag must be 0 or 1")
        tight = flag.value() == 1
    search_stripe(
        Int(e.value()), Int(delta.value()), Int(a.value()),
        Int(lower.value()), Int(upper.value()), min_a, negative, tight
    )
