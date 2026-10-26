"""Generic signed five-term exact verifier, including bases beyond Int64.

Prints arithmetic facts only; novelty and discovery require external review.
Canonical decimal intake is limited to 1024 digits per base as a resource
policy. No floating point, division by zero or narrowing of BigZ values.
"""
from std.sys import argv
from finite_exact.bigint_z import (
    BigZ, bigz_from_i64, bigz_add, bigz_mul, bigz_neg, bigz_gcd
)
from finite_exact.exact_decimal import bigz_decimal


def parse_integer(token: String) raises -> BigZ:
    var data = token.as_bytes()
    if len(data) == 0:
        raise Error("empty candidate integer")
    var start = 0
    var negative = False
    if Int(data[0]) == ord("-"):
        negative = True
        start = 1
    if start == len(data) or len(data)-start > 1024:
        raise Error("candidate decimal outside finite intake policy")
    if len(data)-start > 1 and Int(data[start]) == ord("0"):
        raise Error("noncanonical leading zero")
    var value = bigz_from_i64(0)
    var ten = bigz_from_i64(10)
    for i in range(start, len(data)):
        var digit = Int(data[i])-ord("0")
        if digit < 0 or digit > 9:
            raise Error("candidate integer must be canonical ASCII decimal")
        value = bigz_add(bigz_mul(value, ten), bigz_from_i64(Int64(digit)))
    if negative:
        if value.is_zero():
            raise Error("negative zero is noncanonical")
        value = bigz_neg(value)
    return value^


def fifth(x: BigZ) -> BigZ:
    var square = bigz_mul(x, x)
    return bigz_mul(bigz_mul(square, square), x)


def main() raises:
    var args = argv()
    if len(args) != 6:
        raise Error("usage: verify_candidate x1 x2 x3 x4 x5; sum(x_i^5)=0")
    var residual = bigz_from_i64(0)
    var common = bigz_from_i64(0)
    var nonzero = True
    for i in range(1, 6):
        var x = parse_integer(args[i])
        residual = bigz_add(residual, fifth(x))
        common = bigz_gcd(common, x)
        nonzero = nonzero and not x.is_zero()
    print("RESULT E5-CANDIDATE-v1", bigz_decimal(residual),
          bigz_decimal(common), Int(nonzero))
