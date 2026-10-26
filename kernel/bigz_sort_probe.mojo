"""Actual production Mojo BigZ mergesort conformance records.

IN/OUT rows expose every sum and both pair indices. Outputs are stable
lexicographic sorted permutations; Python independently reconstructs
the full exact tuple list and rejects inserted, lost or changed records.
"""
from finite_exact.bigint_z import (
    BigZ, bigz_from_i64, bigz_add, bigz_mul, bigz_neg
)
from finite_exact.exact_decimal import bigz_decimal
from bigz_pair_index import BigPair, sort_exact_pairs, pair_index_sorted
from euler_exact import fifth_bigz


def emit_case(case_id: Int, mut records: List[BigPair]) raises:
    print("CASE", case_id, len(records))
    for row in records:
        print("IN", bigz_decimal(row.sum), row.a, row.b)
    sort_exact_pairs(records)
    if not pair_index_sorted(records):
        raise Error("production mergesort returned non-ordered records")
    for row in records:
        print("OUT", bigz_decimal(row.sum), row.a, row.b)
    print("END")


def main() raises:
    var huge = bigz_add(bigz_from_i64(9223372036854775807),
                        bigz_from_i64(1))
    var wide = bigz_mul(huge, huge)
    var minus = bigz_neg(wide)
    var empty = List[BigPair]()
    emit_case(0, empty)

    var one = List[BigPair]()
    one.append(BigPair(huge, 1, 1))
    emit_case(1, one)

    var ascending = List[BigPair]()
    for i in range(12):
        ascending.append(BigPair(bigz_from_i64(Int64(i - 5)), i + 1, i + 1))
    emit_case(2, ascending)

    var descending = List[BigPair]()
    for i in range(12):
        descending.append(BigPair(bigz_from_i64(Int64(8 - i)), 12 - i, 12 - i))
    emit_case(3, descending)

    var repeated = List[BigPair]()
    for i in range(16):
        repeated.append(BigPair(huge, 16 - i, 16 - i))
    repeated.append(BigPair(huge, 1, 1))
    repeated.append(BigPair(huge, 1, 1))
    emit_case(4, repeated)

    var mixed = List[BigPair]()
    mixed.append(BigPair(wide, 4, 4))
    mixed.append(BigPair(minus, 1, 1))
    mixed.append(BigPair(huge, 4, 4))
    mixed.append(BigPair(bigz_from_i64(0), 2, 2))
    mixed.append(BigPair(wide, 2, 2))
    mixed.append(BigPair(minus, 3, 3))
    mixed.append(BigPair(huge, 2, 2))
    emit_case(5, mixed)

    var pseudo = List[BigPair]()
    for i in range(64):
        var sum = (i * 37 + 13) % 41 - 20
        pseudo.append(BigPair(bigz_from_i64(Int64(sum)),
                              (i * 11) % 19 + 1, (i * 7) % 23 + 1))
    emit_case(6, pseudo)

    var fifths = List[BigPair]()
    for a in range(1, 13):
        for b in range(a, 13):
            fifths.append(BigPair(
                bigz_add(fifth_bigz(Int64(a)), fifth_bigz(Int64(b))),
                a, b
            ))
    emit_case(7, fifths)
