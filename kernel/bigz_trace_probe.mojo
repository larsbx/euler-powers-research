"""Actual compiled BigZ lower-bound traces with values larger than Int64.

One production implementation drives both traced and untraced calls.
Lean independently replays signed mathematical integers, without
Int64 validation, and Python checks all pair indices and collision runs.
"""
from finite_exact.bigint_z import (
    BigZ, bigz_add, bigz_from_i64, bigz_neg, bigz_mul, bigz_eq
)
from finite_exact.exact_decimal import bigz_decimal
from bigz_pair_index import (
    BigPair, pair_index_sorted, sort_exact_pairs,
    pair_lower_bound, trace_pair_lower_bound, matching_exact_pairs
)


def emit_case(case_id: Int, values: List[BigPair], target: BigZ) raises:
    if not pair_index_sorted(values):
        raise Error("case input not sorted")
    print("CASE", case_id, bigz_decimal(target), len(values))
    for pair in values:
        print("VAL", bigz_decimal(pair.sum))
    var traced = trace_pair_lower_bound(values, target)
    var ordinary = pair_lower_bound(values, target)
    if ordinary != traced:
        raise Error("traced and production lower bounds diverged")
    var present = traced < len(values) and bigz_eq(values[traced].sum, target)
    print("RESULT", traced, 1 if present else 0)
    print("END")


def make_sorted(keys: List[BigZ]) -> List[BigPair]:
    var pairs = List[BigPair]()
    for i in range(len(keys)):
        pairs.append(BigPair(keys[i], i + 1, i + 1))
    sort_exact_pairs(pairs)
    return pairs^


def main() raises:
    var zero = bigz_from_i64(0)
    var one = bigz_from_i64(1)
    var neg7 = bigz_from_i64(-7)
    var huge = bigz_add(
        bigz_from_i64(9223372036854775807), one
    )
    var above = bigz_add(huge, one)
    var negative_huge = bigz_neg(huge)
    var negative_above = bigz_neg(above)
    var huge_square = bigz_mul(huge, huge)

    var empty = List[BigPair]()
    emit_case(0, empty, zero)
    emit_case(1, empty, huge)

    var single = make_sorted([huge])
    emit_case(2, single, bigz_from_i64(9223372036854775807))
    emit_case(3, single, huge)
    emit_case(4, single, above)

    var negatives = make_sorted([
        negative_above, negative_huge, neg7, zero, zero,
        huge, huge, huge, above, huge_square
    ])
    emit_case(5, negatives, negative_above)
    emit_case(6, negatives, negative_huge)
    emit_case(7, negatives, bigz_from_i64(-8))
    emit_case(8, negatives, zero)
    emit_case(9, negatives, one)
    emit_case(10, negatives, huge)
    emit_case(11, negatives, above)
    emit_case(12, negatives, huge_square)
    emit_case(13, negatives, bigz_add(huge_square, one))

    var repeated = List[BigPair]()
    for i in range(33):
        repeated.append(BigPair(huge, i + 1, i + 1))
    emit_case(14, repeated, huge)
    emit_case(15, repeated, above)
    emit_case(16, repeated, negative_huge)

    var mix = make_sorted([
        bigz_from_i64(2), bigz_from_i64(2),
        bigz_from_i64(5), bigz_from_i64(5),
        huge, huge, huge_square
    ])
    emit_case(17, mix, bigz_from_i64(5))
