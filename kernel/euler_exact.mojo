"""Euler-specific exact arithmetic bridge to pinned finite-math-kernels.

Machine operations fail closed on overflow using checked_int; BigZ powers
never narrow into Int64. No runtime assertion here promotes a bounded
search into an unbounded theorem. The consumer owns certificate admission.
"""
from finite_exact.bigint_z import BigZ, bigz_from_i64, bigz_mul
from finite_exact.checked_int import checked_add, checked_sub, checked_mul
from finite_exact.integer_gcd import gcd_i64


def fifth_int(x: Int) raises -> Int64:
    """Fifth power if representable in signed Int64; otherwise raise."""
    var result = x
    for _ in range(4):
        result = checked_mul(result, x)
    return Int64(result)


def pair_sum(x: Int64, y: Int64) raises -> Int64:
    return Int64(checked_add(Int(x), Int(y)))


def complement(target: Int64, c: Int64, d: Int64) raises -> Int64:
    return Int64(checked_sub(checked_sub(Int(target), Int(c)), Int(d)))


def checked_pack_pair(value: Int64, a: Int, b: Int, stride: Int) raises -> Int64:
    """Lossless pair encoding for nonnegative values and 0<=digits<stride."""
    if value < 0 or stride < 2 or a < 0 or b < 0 or a >= stride or b >= stride:
        raise Error("packed pair outside canonical digit domain")
    var left = checked_add(checked_mul(Int(value), stride), a)
    return Int64(checked_add(checked_mul(left, stride), b))


def primitive5(a: Int64, b: Int64, c: Int64, d: Int64, e: Int64) raises -> Bool:
    var g = gcd_i64(a, b)
    g = gcd_i64(g, c)
    g = gcd_i64(g, d)
    g = gcd_i64(g, e)
    return g == 1


def fifth_bigz(x: Int64) -> BigZ:
    """Arbitrary-precision fifth power, including negative input."""
    var base = bigz_from_i64(x)
    var result = bigz_from_i64(1)
    for _ in range(5):
        result = bigz_mul(result, base)
    return result^
