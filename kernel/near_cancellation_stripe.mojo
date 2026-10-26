"""Novelty-territory exact E5 near-cancellation stripe (Mojo, BigZ).

For fixed e, delta=e-d and a<=A, search ALL admissible ordered pairs
(a,c) in a declared contiguous c interval. The full c interval follows
from c^5 <= D=e^5-d^5 <= 3c^5. A stripe is never a height-complete census.

The only modular rejection is the complete fifth-power image of b<=c;
final witnesses require exact fifth powers and five-way primitive gcd.
No floating point, heuristic rounding or packed sum used.
"""
from std.sys import argv
from certified_records.codec import parse_canonical
from finite_exact.bigint_z import (
    BigZ, bigz_from_i64, bigz_sub, bigz_lt, bigz_eq
)
from finite_polynomial.polynomial_fp import Modulus
from euler_exact import fifth_bigz, primitive5
from near_cancellation import (
    max_fifth_root, min_three_fifth_root, b_fifth_lower_bound
)


def search_stripe(
    e: Int, delta: Int, max_a: Int, c_start: Int, c_end: Int
) raises:
    # Resource policy, not a mathematical upper bound on E5.
    if (e < 5 or e > 4000000 or delta < 1 or delta > 256 or
        delta >= e or max_a < 1 or max_a > 64 or
        c_start < 1 or c_start > c_end or c_end >= e or
        c_end - c_start >= 4096 or c_end > 600000):
        raise Error("E5STRIPE range or explicit resource budget exceeded")
    var d = e - delta
    var remainder = bigz_sub(
        fifth_bigz(Int64(e)), fifth_bigz(Int64(d))
    )
    var c_min = min_three_fifth_root(remainder, d)
    var c_max = max_fifth_root(remainder, d)
    if c_start < c_min or c_end > c_max:
        raise Error("stripe exceeds mathematically admissible c bounds")

    print("DOMAIN E5STRIPEv1", e, delta, max_a, c_start, c_end)
    print("BOUNDS", c_min, c_max, d)

    # Cache *exact* fifth powers up to the right edge. Memory O(c_end).
    # The complete modular b-image is built independently from every
    # 1<=b<=c, not an assumed prime-field/CRT distribution.
    var powers = List[BigZ]()
    for b in range(c_end + 1):
        powers.append(fifth_bigz(Int64(b)))
    var ring = Modulus(99000)
    var fifth_seen = List[Bool](length=99000, fill=False)
    for b in range(1, c_start):
        fifth_seen[ring.pow(b, 5)] = True

    var trials = 0
    var rejected = 0
    var lookups = 0
    var witnesses = 0
    for c in range(c_start, c_end + 1):
        fifth_seen[ring.pow(c, 5)] = True
        var left = bigz_sub(remainder, powers[c])
        for a in range(1, min(c, max_a) + 1):
            trials += 1
            var candidate = bigz_sub(left, powers[a])
            if candidate.sign <= 0:
                rejected += 1
                continue
            if not fifth_seen[ring.reduce_bigz(candidate)]:
                rejected += 1
                continue
            lookups += 1
            var b = b_fifth_lower_bound(powers, candidate, a, c)
            if b <= c and bigz_eq(powers[b], candidate):
                if primitive5(Int64(a), Int64(b), Int64(c),
                              Int64(d), Int64(e)):
                    # All terms are already positive/order constrained.
                    # Recheck exact identity at the admission boundary.
                    var lhs = fifth_bigz(Int64(e))
                    var computed = bigz_sub(lhs, powers[c])
                    computed = bigz_sub(computed, powers[a])
                    computed = bigz_sub(computed, powers[b])
                    if not bigz_eq(computed, fifth_bigz(Int64(d))):
                        raise Error("BigZ stripe candidate failed exact identity")
                    print("CERT E5v1", a, b, c, d, e)
                    witnesses += 1
    print("SUMMARY", c_end - c_start + 1,
          trials, rejected, lookups, witnesses)


def main() raises:
    var args = List[String]()
    for arg in argv():
        args.append(String(arg))
    if len(args) != 6:
        raise Error("usage: near_cancellation_stripe E DELTA A C_LO C_HI")
    var e = parse_canonical(args[1], 32)
    var delta = parse_canonical(args[2], 32)
    var a = parse_canonical(args[3], 32)
    var lower = parse_canonical(args[4], 32)
    var upper = parse_canonical(args[5], 32)
    if not e or not delta or not a or not lower or not upper:
        raise Error("noncanonical integer search stripe")
    search_stripe(
        Int(e.value()), Int(delta.value()), Int(a.value()),
        Int(lower.value()), Int(upper.value())
    )
