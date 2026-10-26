"""Deterministic finite arithmetic conformance transcript; not an E5 search."""
from finite_exact.bigint_z import bigz_from_i64
from finite_exact.exact_decimal import bigz_decimal
from cyclotomic5 import Cyclotomic5, from_i64, add, sub, mul, conjugate, norm


def vector(index: Int) -> Cyclotomic5:
    var value = index
    var out = Cyclotomic5()
    for i in range(4):
        out.coefficients[i] = bigz_from_i64(Int64(value % 3 - 1))
        value = value // 3
    return out^


def emit(label: String, i: Int, j: Int, x: Cyclotomic5):
    print(label, i, j, bigz_decimal(x.coefficients[0]),
          bigz_decimal(x.coefficients[1]), bigz_decimal(x.coefficients[2]),
          bigz_decimal(x.coefficients[3]))


def main() raises:
    print("DOMAIN E5-CYCLOTOMIC5-v1 81 81 4 16")
    for i in range(81):
        var x = vector(i)
        for j in range(81):
            var y = vector(j)
            emit("ADD", i, j, add(x, y))
            emit("SUB", i, j, sub(x, y))
            emit("MUL", i, j, mul(x, y))
        for k in range(1, 5):
            emit("AUTO", i, k, conjugate(x, k))
        print("NORM", i, bigz_decimal(norm(x)))
    # Cross Int64 by many orders of magnitude without narrowing a BigZ result.
    var big = from_i64(1, -1, 1, -1)
    for i in range(16):
        big = mul(big, from_i64(1000000000, 1, -1, 2))
        emit("BIG", i, 0, big)
        print("BIGNORM", i, bigz_decimal(norm(big)))
    # Signed and zero edge cases, the four known identities' (e,d) pairs,
    # and current post-Braun target/gap controls (no solution claim).
    var xs: List[Int64] = [0, 1, -1, 144, 14132, 85359, 1956878, 2760001]
    var ys: List[Int64] = [0, 1, 2, 133, 14068, 85282, 1956213, 2759745]
    for i in range(len(xs)):
        print("DIFFNORM", i, xs[i], ys[i], bigz_decimal(norm(from_i64(xs[i], -ys[i]))))
        print("SUMNORM", i, xs[i], ys[i], bigz_decimal(norm(from_i64(xs[i], ys[i]))))
    var rejected = 0
    for k in [0, 5, -1]:
        try:
            _ = conjugate(from_i64(1), k)
        except:
            rejected += 1
    var bad = Cyclotomic5()
    bad.coefficients.append(bigz_from_i64(0))
    try:
        _ = mul(bad, from_i64(1))
    except:
        rejected += 1
    if rejected != 4:
        raise Error("invalid arithmetic input was accepted")
    print("REJECTED", rejected)
    print("END E5-CYCLOTOMIC5-v1")
