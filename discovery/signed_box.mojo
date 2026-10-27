"""Complete sorted signed five-term boxes, oriented by positive median.

BigZ stores all powers, targets, pair sums and coverage checksums. Int stores
only bounded indices/counts. No modular sieve or floating approximation.
"""
from std.sys import argv
from finite_exact.bigint_z import BigZ, bigz_from_i64, bigz_add, bigz_neg, bigz_eq
from finite_exact.exact_decimal import bigz_decimal
from euler_exact import fifth_bigz
from verify_known import decimal_base
from bigz_pair_index import BigPair, sort_exact_pairs, matching_exact_pairs
from pair_sum import reconstructed_pairs


def main() raises:
    var args = argv()
    if len(args) != 7:
        raise Error("usage: signed_box index|reconstruct N c_low c_high small_count high_start")
    var method = args[1]
    var bound = Int(decimal_base(args[2]))
    var low = Int(decimal_base(args[3]))
    var high = Int(decimal_base(args[4]))
    var small = Int(decimal_base(args[5]))
    var high_start = Int(decimal_base(args[6]))
    if small < 0 or small > bound or high_start < 1 or high_start > 1000000000 or (small < bound and high_start <= small):
        raise Error("invalid magnitude bands")
    if (method != "index" and method != "reconstruct") or bound < 1 or bound > 1024 or low < 1 or high < low or high > bound:
        raise Error("outside reviewed finite signed domain")
    if method == "reconstruct" and (bound > 32 or small != bound):
        raise Error("reconstruction restricted to strategy comparison")
    var bases = List[Int]()
    for i in range(-bound, bound+1):
        var value = abs(i)
        if value > small:
            value = high_start+value-small-1
        if i < 0:
            value = -value
        bases.append(value)
    var powers = List[BigZ]()
    for x in bases:
        powers.append(fifth_bigz(Int64(x)))
    var pairs = List[BigPair]()
    if method == "index":
        for a in range(-bound, 0):
            # a<=b, b!=0, a+b<0; exactly all negative-sum pairs.
            for b in range(a, -a):
                if b != 0:
                    pairs.append(BigPair(bigz_add(powers[a+bound], powers[b+bound]), a, b))
        sort_exact_pairs(pairs)
        if len(pairs) != bound*bound:
            raise Error("pair-domain cardinality mismatch")
    print("DOMAIN E5-SIGNED-BOX-v1", method, bound, low, high, small, high_start, len(pairs))
    var total = 0
    var hits = 0
    for c in range(low, high+1):
        var count = 0
        var row_hits = 0
        var checksum = bigz_from_i64(0)
        for d in range(c, bound+1):
            var cd = bigz_add(powers[c+bound], powers[d+bound])
            for e in range(d, bound+1):
                var target = bigz_neg(bigz_add(cd, powers[e+bound]))
                checksum = bigz_add(checksum, target)
                var found = List[Tuple[Int, Int]]()
                if method == "index":
                    found = matching_exact_pairs(pairs, target, c)
                else:
                    var result = reconstructed_pairs(target, bound)
                    for pair in result[0]:
                        if pair[1] <= c and pair[0] != 0 and pair[1] != 0:
                            found.append(pair)
                for pair in found:
                    var a = pair[0]
                    var b = pair[1]
                    # Explicit nontriviality filter; all five bases nonzero.
                    if a == -b or a == -c or a == -d or a == -e or b == -c or b == -d or b == -e:
                        continue
                    if not bigz_eq(bigz_add(powers[a+bound], powers[b+bound]), target):
                        raise Error("indexed hit failed exact equality")
                    print("HIT", bases[a+bound], bases[b+bound], bases[c+bound], bases[d+bound], bases[e+bound])
                    row_hits += 1
                count += 1
        print("ROW", c, count, row_hits, bigz_decimal(checksum))
        total += count
        hits += row_hits
    print("COMPLETE", total, hits)
