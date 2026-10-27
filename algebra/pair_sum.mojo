"""Bounded exact reconstruction of signed fifth-power pairs; no factor oracle.

All pairs -B<=a<=b<=B are covered. Zero entries are allowed here; an Euler
caller must impose its own positivity/nonzero/primitivity requirements.
The full candidate sum interval is enumerated, so no incomplete integer
factorization is promoted into a coverage assertion.
"""
from finite_exact.bigint_z import (
    BigZ, bigz_from_i64, bigz_add, bigz_sub, bigz_mul, bigz_lt, bigz_eq, bigz_divmod
)
from euler_exact import fifth_bigz


def square_root_if_exact(value: BigZ, upper: Int) raises -> Int:
    if upper < 0 or upper > 10000000000:
        raise Error("square-root bound outside reviewed machine domain")
    if value.sign < 0:
        return -1
    var lo = 0
    var hi = upper+1
    while lo < hi:
        var mid = lo+(hi-lo)//2
        var base = bigz_from_i64(Int64(mid))
        if bigz_lt(bigz_mul(base, base), value):
            lo = mid+1
        else:
            hi = mid
    if lo <= upper:
        var base = bigz_from_i64(Int64(lo))
        if bigz_eq(bigz_mul(base, base), value):
            return lo
    return -1


def check_bound(bound: Int) raises:
    # This cap proves all s*s, 10*B*B, p numerators and (a-b)^2 fit Int.
    # Fifth powers, target arithmetic and discriminants remain BigZ.
    if bound < 1 or bound > 16384:
        raise Error("pair box outside reviewed finite resource domain")


def reconstructed_pairs(target: BigZ, bound: Int) raises -> Tuple[List[Tuple[Int, Int]], Int, Int, Int]:
    check_bound(bound)
    var out = List[Tuple[Int, Int]]()
    var trials = 0
    var divisors = 0
    var squares = 0
    var matches = 0
    if target.is_zero():
        # Exactly the finite family a=-b in this ordered signed box.
        for a in range(-bound, 1):
            out.append((a, -a))
            matches += 1
        return (out^, trials, divisors, squares)
    for s in range(-2*bound, 2*bound+1):
        if s == 0:
            continue
        trials += 1
        var division = bigz_divmod(target, bigz_from_i64(Int64(s)))
        if division.rejected:
            raise Error("nonzero divisor unexpectedly rejected")
        if not division.remainder.is_zero():
            continue
        divisors += 1
        var ss = bigz_from_i64(Int64(s*s))
        var delta = bigz_add(bigz_mul(bigz_from_i64(5), bigz_mul(ss, ss)),
                             bigz_mul(bigz_from_i64(20), division.quotient))
        # For a valid pair sqrt(delta)=5*(a^2+b^2)<=10*B^2.
        var root = square_root_if_exact(delta, 10*bound*bound)
        if root < 0:
            continue
        squares += 1
        var numerator = 5*s*s-root
        if numerator % 10 != 0:
            continue
        var p = numerator // 10
        var diff = square_root_if_exact(bigz_from_i64(Int64(s*s-4*p)), 2*bound)
        if diff < 0 or (s-diff) % 2 != 0:
            continue
        var a = (s-diff)//2
        var b = (s+diff)//2
        if a < -bound or b > bound:
            continue
        if not bigz_eq(bigz_add(fifth_bigz(Int64(a)), fifth_bigz(Int64(b))), target):
            raise Error("reconstruction failed final exact fifth-power equality")
        out.append((a, b))
        matches += 1
    return (out^, trials, divisors, squares)


def reconstruct(target: BigZ, bound: Int) raises:
    var result = reconstructed_pairs(target, bound)
    for pair in result[0]:
        print("PAIR", pair[0], pair[1])
    print("SUMMARY", result[1], result[2], result[3], len(result[0]))


def scan(target: BigZ, bound: Int) raises:
    """Baseline: all a, exact sorted fifth-power table and binary b membership."""
    check_bound(bound)
    var powers = List[BigZ]()
    for x in range(-bound, bound+1):
        powers.append(fifth_bigz(Int64(x)))
    var matches = 0
    for a in range(-bound, bound+1):
        var needed = bigz_sub(target, powers[a+bound])
        var lo = a+bound
        var hi = len(powers)
        while lo < hi:
            var mid = lo+(hi-lo)//2
            if bigz_lt(powers[mid], needed):
                lo = mid+1
            else:
                hi = mid
        if lo < len(powers) and bigz_eq(powers[lo], needed):
            print("PAIR", a, lo-bound)
            matches += 1
    print("SUMMARY", 2*bound+1, matches)
