"""Shared production helpers tested with synthetic collisions and equal residues."""
from pair_partition import key, build_buckets, matching_pairs
from pair_partition import build_indexed_buckets, matching_indexed_pairs, pack_pair


def main():
    var moduli: List[Int] = [1, 2, 7, 11, 35]
    for m in moduli:
        for s in range(71):
            for t in range(71):
                var k = key(Int64(s), Int64(t), m)
                print("KEY", m, s, t, k[0], k[1])
    # Synthetic powers deliberately collide: target=5 has (1,4),(2,3).
    # These are helper tests, not fifth-power certificates.
    var powers: List[Int64] = [0, 1, 2, 3, 4]
    for m in moduli:
        var buckets = build_buckets(powers, 5, m)
        for r in range(m):
            for value in buckets[r]:
                print("BUCKET", m, r, value)
    for c in range(1, 5):
        for target in range(10):
            var pairs = matching_pairs(powers, Int64(target), c)
            for p in pairs:
                print("PAIR", c, target, p[0], p[1])

    # The new PRODUCTION indexed lookup must retain distinct colliding
    # representations and all equal-valued synthetic-power combinations.
    var repeated: List[Int64] = [0, 2, 2, 5, 5]
    for m in moduli:
        var index_a = build_indexed_buckets(powers, 5, m)
        var index_b = build_indexed_buckets(repeated, 5, m)
        for c in range(1, 5):
            for target in range(13):
                var first = matching_indexed_pairs(
                    index_a[Int(Int64(target) % Int64(m))],
                    Int64(target), c, 145
                )
                for p in first:
                    print("INDEX", 0, m, c, target, p[0], p[1])
                var second = matching_indexed_pairs(
                    index_b[Int(Int64(target) % Int64(m))],
                    Int64(target), c, 145
                )
                for p in second:
                    print("INDEX", 1, m, c, target, p[0], p[1])
    # Large-bound safety witness tests near the edge of the packed range.
    print("PACK", pack_pair(Int64(2) * Int64(144) * Int64(144) * Int64(144) * Int64(144) * Int64(144), 143, 143, 145))
