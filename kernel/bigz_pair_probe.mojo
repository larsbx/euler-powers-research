"""Native BigZ pair-index conformance, including >Int64 keys and collisions."""
from finite_exact.bigint_z import (
    BigZ, bigz_from_i64, bigz_add
)
from finite_exact.exact_decimal import bigz_decimal
from bigz_pair_index import (
    BigPair, pair_less, sort_exact_pairs, pair_lower_bound,
    matching_exact_pairs, indexed_exact_pairs, pair_index_sorted
)


def main() raises:
    var powers = List[BigZ]()
    for n in [0, 1, 2, 3, 4]:
        powers.append(bigz_from_i64(Int64(n)))
    var index = indexed_exact_pairs(powers, 5)
    if not pair_index_sorted(index):
        raise Error("small synthetic index unordered")
    var target = bigz_from_i64(5)
    var pairs = matching_exact_pairs(index, target, 4)
    for p in pairs:
        print("COLLISION", p[0], p[1])
    var narrow = matching_exact_pairs(index, target, 2)
    for p in narrow:
        print("NARROW", p[0], p[1])
    var huge = bigz_add(
        bigz_from_i64(9223372036854775807), bigz_from_i64(1)
    )
    var above = bigz_add(huge, bigz_from_i64(1))
    var records = List[BigPair]()
    records.append(BigPair(above, 3, 3))
    records.append(BigPair(huge, 2, 2))
    records.append(BigPair(bigz_from_i64(-7), 1, 1))
    records.append(BigPair(huge, 1, 2))
    records.append(BigPair(huge, 1, 1))
    records.append(BigPair(bigz_from_i64(0), 2, 2))
    sort_exact_pairs(records)
    if not pair_index_sorted(records) or pair_lower_bound(records, huge) != 2:
        raise Error("multi-limb sort/lower_bound failed")
    for row in records:
        print("RECORD", bigz_decimal(row.sum), row.a, row.b)
    var recovered = matching_exact_pairs(records, huge, 2)
    for p in recovered:
        print("HUGEPAIR", p[0], p[1])
    if len(recovered) != 3:
        raise Error("same-sum representations lost")
    print("BIGGER", bigz_decimal(above))
